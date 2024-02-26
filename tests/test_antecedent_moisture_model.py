#!/usr/bin/env python

"""Tests for `antecedent_moisture_model` package."""
from pathlib import Path

import pytest
import numpy as np
import pandas as pd

from antecedent_moisture_model.antecedent_moisture_model import (
    run_multicomponent_antecedent_moisture_model,
)
from antecedent_moisture_model.datatypes.units import (
    convert_units,
    INTERNAL_UNITS_TIME,
    INTERNAL_UNITS_AREA,
    INTERNAL_UNITS_TEMPERATURE,
    INTERNAL_UNITS_PRECIP,
    INTERNAL_UNITS_FLOW,
)
from antecedent_moisture_model.timeseries.timeseries import (
    VARNAMES_INTERMEDIATE,
    VARNAMES_FLOW,
)

base_input_path = Path("tests/data")


def test_spreadsheet_tab20_param_initialization_gives_correct_values():
    input_path = Path(base_input_path, "spreadsheet_tab20")
    mcamm = run_multicomponent_antecedent_moisture_model(
        input_path, num_timesteps_to_run=0
    )
    component = mcamm.amm_components[0]

    assert mcamm.timestep == pytest.approx(
        convert_units("HOURS", INTERNAL_UNITS_TIME, 1)
    )
    assert component.catchment_area == pytest.approx(
        convert_units("ACRES", INTERNAL_UNITS_AREA, 4000)
    )
    assert component.hydrograph_half_life_time == pytest.approx(
        convert_units("HOURS", INTERNAL_UNITS_TIME, 22.76)
    )
    assert component.dry_weather_capture_fraction == pytest.approx(0.01)
    assert component.antecedent_moisture_half_life_time == pytest.approx(
        convert_units("HOURS", INTERNAL_UNITS_TIME, 48.0)
    )
    assert component.precip_averaging_time == pytest.approx(
        convert_units("HOURS", INTERNAL_UNITS_TIME, 1)
    )
    assert component.temperature_averaging_time == pytest.approx(
        convert_units("HOURS", INTERNAL_UNITS_TIME, 240)
    )
    assert component.cold_temperature == pytest.approx(
        convert_units("FAHRENHEIT", INTERNAL_UNITS_TEMPERATURE, 30)
    )
    assert component.hot_temperature == pytest.approx(
        convert_units("FAHRENHEIT", INTERNAL_UNITS_TEMPERATURE, 70)
    )
    assert component.addl_capture_fraction_cold == pytest.approx(0.05)
    assert component.addl_capture_fraction_hot == pytest.approx(0.01)
    assert component.shape_factor == pytest.approx(0.970, rel=0.001)
    assert component.antecedent_moisture_retention_factor == pytest.approx(
        0.986, rel=0.001
    )
    assert component.moving_avg_steps_precip == pytest.approx(2, rel=0.001)
    assert component.moving_avg_steps_temperature == pytest.approx(
        241, rel=0.001
    )
    assert component.time_to_peak == pytest.approx(
        convert_units("HOURS", INTERNAL_UNITS_TIME, 2), rel=0.001
    )
    assert component.sigmoid_max == pytest.approx(0.048, rel=0.001)
    assert component.sigmoid_steepness == pytest.approx(-0.1199, rel=0.001)
    assert component.sigmoid_midpoint == pytest.approx(50, rel=0.001)


tab_20_units = {
    "temperature": "FAHRENHEIT",
    "precip": "INCHES",
    "flow": "CUBICFEETPERSECOND",
}


def test_spreadsheet_tab20_example_simulated_variables_give_correct_values():
    input_path = Path(base_input_path, "spreadsheet_tab20")
    mcamm = run_multicomponent_antecedent_moisture_model(input_path)
    component = mcamm.amm_components[0]

    raw_input_data = pd.read_csv(
        Path(mcamm.input_path, mcamm.input_data_config.input_data_file),
        skiprows=mcamm.input_data_config.skip_rows,
    )

    for var in VARNAMES_INTERMEDIATE + VARNAMES_FLOW:
        converted_expected_total = get_expected_total_from_raw_data(
            var, raw_input_data, tab_20_units, mcamm
        )
        assert component.__getattribute__(var).sum() == pytest.approx(
            converted_expected_total,
            rel=0.001,
        )


def get_expected_total_from_raw_data(
    var, raw_input_data, raw_data_units, mcamm
):
    expected_total = raw_input_data[
        mcamm.input_data_config.__getattribute__(f"{var}_colname")
    ]
    if "temperature" in var:
        converted_expected_total = convert_units(
            raw_data_units["temperature"],
            INTERNAL_UNITS_TEMPERATURE,
            expected_total,
        )
    elif "precip" in var:
        converted_expected_total = convert_units(
            raw_data_units["precip"],
            INTERNAL_UNITS_PRECIP,
            expected_total,
        )
    elif "flow" in var:
        converted_expected_total = convert_units(
            raw_data_units["flow"],
            INTERNAL_UNITS_FLOW,
            expected_total,
        )
    else:
        converted_expected_total = expected_total
    return converted_expected_total.sum()


def test_spreadsheet_tab20_flow_plot():
    input_path = Path(base_input_path, "spreadsheet_tab20")
    mcamm = run_multicomponent_antecedent_moisture_model(
        input_path,
        figure_filename="results.png",
        export_filename="results.csv",
    )


tab_20_different_units = {
    "temperature": "CELSIUS",
    "precip": "CENTIMETERS",
    "flow": "CUBICMETERSPERSECOND",
}


def test_spreadsheet_tab20_different_units_simulated_variables_give_correct_values():
    input_path = Path(base_input_path, "spreadsheet_tab20_different_units")
    mcamm = run_multicomponent_antecedent_moisture_model(
        input_path,
        figure_filename="results.png",
        export_filename="results.csv",
    )
    component = mcamm.amm_components[0]

    raw_input_data = pd.read_csv(
        Path(mcamm.input_path, mcamm.input_data_config.input_data_file),
        skiprows=mcamm.input_data_config.skip_rows,
    )

    for var in VARNAMES_INTERMEDIATE + VARNAMES_FLOW:
        converted_expected_total = get_expected_total_from_raw_data(
            var, raw_input_data, tab_20_different_units, mcamm
        )
        assert component.__getattribute__(var).sum() == pytest.approx(
            converted_expected_total,
            rel=0.001,
        )


def test_spreadsheet_tab20_21_multicomponent_simulated_variables():
    input_path = Path(base_input_path, "spreadsheet_tab20-21")
    mcamm = run_multicomponent_antecedent_moisture_model(
        input_path,
        figure_filename="results.png",
        export_filename="results.csv",
    )
    raw_input_data = pd.read_csv(
        Path(mcamm.input_path, mcamm.input_data_config.input_data_file),
        skiprows=mcamm.input_data_config.skip_rows,
    )
    var = "flow"
    converted_expected_total = get_expected_total_from_raw_data(
        var, raw_input_data, tab_20_units, mcamm
    )
    assert mcamm.__getattribute__(var).sum() == pytest.approx(
        converted_expected_total,
        rel=0.001,
    )


def test_noisy_example_multicomponent_flow_realistic():
    input_path = Path(base_input_path, "noisy_example")
    mcamm = run_multicomponent_antecedent_moisture_model(
        input_path,
        figure_filename="results.png",
        zoom_indices=[40000, 45000],
        export_filename="results.csv",
    )
    assert mcamm.flow[-1] > 0
    assert sum(mcamm.flow < 0) == 0


def test_noisy_example_multicomponent_partial_run_flow_realistic():
    input_path = Path(base_input_path, "noisy_example")
    starting_timestep = 2 * 30 * 24 * 12  # start 2 months in
    initial_conditions = {
        "baseflow": {"total_capture_fraction": 0.1, "flow": 2},
        "rdii": {"total_capture_fraction": 0.1, "flow": 2},
    }
    num_timesteps_to_run = starting_timestep * 2
    mcamm = run_multicomponent_antecedent_moisture_model(
        input_path,
        starting_timestep,
        initial_conditions,
        num_timesteps_to_run,
        figure_filename="results.png",
        export_filename="results.csv",
    )
    # check that flow is zero everywhere except in simulated range
    amm_flow = mcamm.flow - mcamm.amm_components[0].flow
    nonzero_flow_timesteps = np.where(amm_flow > 0)[0]
    assert nonzero_flow_timesteps[0] == starting_timestep - 1
    assert (
        nonzero_flow_timesteps[-1] - nonzero_flow_timesteps[0]
        == num_timesteps_to_run
    )
    # check flow initialiized properly
    amm_flow[nonzero_flow_timesteps[0]] == pytest.approx(
        sum([initial_conditions[c]["flow"] for c in initial_conditions])
    )
