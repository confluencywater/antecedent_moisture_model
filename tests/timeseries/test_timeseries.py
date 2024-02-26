from pathlib import Path

import pandas as pd
import pytest
import yaml

from antecedent_moisture_model.timeseries.datamodel import InputDataConfig
from antecedent_moisture_model.timeseries.timeseries import (
    TimeseriesSetup,
)
from antecedent_moisture_model.timeseries.exceptions import (
    InvalidOrMissingTimestampException,
    MissingDataColumnException,
)

base_input_path = Path("tests/data")


def prepare_input_data(input_data_config_path: Path, timestep_hours: int = 0):
    input_data_config_dict = yaml.safe_load(open(input_data_config_path, "r"))
    input_data_config = InputDataConfig(**input_data_config_dict)

    input_data = pd.read_csv(
        Path(
            input_data_config_path.parent,
            input_data_config.input_data_file,
        ),
        skiprows=input_data_config.skip_rows,
    )

    prepared_data = TimeseriesSetup(
        input_data, input_data_config, timestep_hours
    ).run()
    return prepared_data


def test_input_data_invalid_timestamp():
    input_data_config_path = Path(
        base_input_path, "invalid_timestamp", "input_data_config.yaml"
    )
    with pytest.raises(InvalidOrMissingTimestampException):
        input_dict = prepare_input_data(input_data_config_path)


def test_input_data_missing_precip():
    input_data_config_path = Path(
        base_input_path, "missing_precip", "input_data_config.yaml"
    )
    with pytest.raises(MissingDataColumnException):
        input_dict = prepare_input_data(input_data_config_path)


def test_input_data_missing_flow():
    input_data_config_path = Path(
        base_input_path, "missing_flow", "input_data_config.yaml"
    )
    with pytest.raises(MissingDataColumnException):
        input_dict = prepare_input_data(input_data_config_path)


def test_input_data_spreadsheet_tab20():
    input_data_config_path = Path(
        base_input_path, "spreadsheet_tab20", "input_data_config.yaml"
    )
    input_dict = prepare_input_data(input_data_config_path)
