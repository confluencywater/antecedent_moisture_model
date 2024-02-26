"""Main module."""

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import yaml

from .datatypes.units import (
    convert_units,
    INTERNAL_UNITS_TIME,
)
from .postprocess.dataexport import export_to_csv
from .postprocess.plotter import plot_simulated_results
from .simulator.dwf import DWFSimulator
from .simulator.amm_baseflow import AMMBaseflowSimulator
from .simulator.amm_rdii import (
    AMMRDIISimulator,
)
from .simulator.config_override_functions import (
    override_components_to_include,
    override_component_params,
)
from .timeseries.timeseries import (
    setup_timeseries,
    InputDataConfig,
)


COMPONENT_CLASSES = {
    "dwf": DWFSimulator,
    "baseflow": AMMBaseflowSimulator,
    "rdii": AMMRDIISimulator,
}


class AntecedentMoistureModel:
    def __init__(
        self,
        input_path: Path,
        input_data_config_file: str = "input_data_config.yaml",
        simulation_config_file: str = "simulation_config.yaml",
        components_to_include_override=None,
        params_to_override_labels=None,
        params_to_override_values=None,
    ) -> None:

        self.input_path = input_path
        self.input_data_config_file = input_data_config_file

        simulation_config_path = Path(input_path, simulation_config_file)
        simulation_config_dict = yaml.safe_load(
            open(simulation_config_path, "r")
        )

        self.timestep = convert_units(
            simulation_config_dict["timestep_units"],
            INTERNAL_UNITS_TIME,
            float(simulation_config_dict["timestep"]),
        )
        assert self.timestep > 0.0

        self._load_timeseries()

        self.component_labels = override_components_to_include(
            components_to_include_override, simulation_config_dict
        )

        self.amm_components = []
        self.num_amm_components = 0
        for component in self.component_labels:
            component_param_config_dict = simulation_config_dict["components"][
                component
            ]
            component_param_config_dict = override_component_params(
                component,
                component_param_config_dict,
                params_to_override_labels,
                params_to_override_values,
            )
            ComponentClass = COMPONENT_CLASSES[
                component_param_config_dict["component_type"]
            ]
            amm = ComponentClass(
                component_param_config_dict,
                self.input_data["precip"],
                self.input_data["temperature"],
                self.timestep,
            )
            self.amm_components.append(amm)
            self.num_amm_components += 1

    def _load_timeseries(self) -> None:
        input_data_config_dict = yaml.safe_load(
            open(Path(self.input_path, self.input_data_config_file), "r")
        )
        self.input_data_config = InputDataConfig(**input_data_config_dict)

        self.input_data = setup_timeseries(
            pd.read_csv(
                Path(self.input_path, self.input_data_config.input_data_file),
                skiprows=self.input_data_config.skip_rows,
            ),
            self.input_data_config,
            self.timestep,
        )
        self.num_timesteps_input_data = len(self.input_data["timestamp"])

    def run(
        self,
        starting_timestep: int = 1,
        initial_conditions: Dict[str, float] = None,
        num_timesteps_to_run=None,
    ) -> None:
        """
        This is the core simulation call after the AMM has been initialized/setup.
        The simulation is run in vectorized fashion over a specified interval with
        specified initial conditions.

        Args:
            starting_timestep (int): index/timestep to start simulation
            initial_conditions: Dict
                <component1_label>: Dict
                    total_capture_fraction (float): value of total_capture_fraction on timestep = (starting_timestep - 1)
                    flow (float): value of flow on timestep = (starting_timestep - 1)
                <component2_label>: Dict
                    total_capture_fraction (float): value of total_capture_fraction on timestep = (starting_timestep - 1)
                    flow (float): value of flow on timestep = (starting_timestep - 1)
            num_timesteps_to_run (int): number of timesteps (integer index) to simulate forward from starting_timestep
        """

        self.flow = np.zeros(self.num_timesteps_input_data)
        for component_label, component in zip(
            self.component_labels, self.amm_components
        ):
            if initial_conditions is not None:
                component_initial_conditions = initial_conditions.get(
                    component_label, None
                )
            else:
                component_initial_conditions = None
            component.run(
                starting_timestep,
                component_initial_conditions,
                num_timesteps_to_run,
            )
            self.flow += component.flow

    def plot_results(
        self, figure_filename: str = "results.png", zoom_indices=None
    ) -> None:
        plot_simulated_results(
            self.component_labels,
            self.input_data,
            self.amm_components,
            self.flow,
            figure_filename,
            zoom_indices=zoom_indices,
        )

    def export_to_csv(self, export_filename: str = "results.csv") -> None:
        export_to_csv(
            self.component_labels,
            self.input_data,
            self.amm_components,
            self.flow,
            export_filename,
        )


def run_multicomponent_antecedent_moisture_model(
    input_path,
    starting_timestep: int = 1,
    initial_conditions: Dict = None,
    num_timesteps_to_run: int = None,
    figure_filename: str = None,
    zoom_indices: List[int] = None,
    export_filename: str = None,
) -> AntecedentMoistureModel:

    mcamm = AntecedentMoistureModel(input_path)

    mcamm.run(starting_timestep, initial_conditions, num_timesteps_to_run)

    if figure_filename is not None:
        mcamm.plot_results(Path(input_path, figure_filename), zoom_indices)
    if export_filename is not None:
        mcamm.export_to_csv(Path(input_path, export_filename))

    return mcamm
