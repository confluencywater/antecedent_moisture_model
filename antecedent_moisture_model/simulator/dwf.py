from typing import Dict

import numpy as np
from pydantic import BaseModel, NonNegativeFloat, confloat, field_validator

from ..datatypes.units import (
    convert_units,
    units_options_dict,
    INTERNAL_UNITS_TIME,
    INTERNAL_UNITS_FLOW,
)


class DWFConfig(BaseModel):
    base_wastewater_flow: NonNegativeFloat = 0.0
    flow_units: str = "CUBICFEETPERSECOND"
    sin_t_shift_hours: confloat(ge=0.0, lt=24.0) = 0.0
    time_parameters_units: str = "HOURS"
    sin_amplitude_fraction: confloat(ge=0.0, le=1.0) = 0.0

    @field_validator("time_parameters_units")
    def validate_time_parameters_units(cls, v):
        assert v in units_options_dict["time"]
        return v

    @field_validator("flow_units")
    def validate_flow_units(cls, v):
        assert v in units_options_dict["flow"]
        return v


class DWFSimulator:
    def __init__(
        self,
        component_config_dict: Dict,
        precip: np.ndarray,
        temperature: np.ndarray,
        timestep: float,
    ) -> None:

        self.timestep = timestep
        self.num_timesteps_input_data = len(precip)

        self.component_config = DWFConfig(
            **component_config_dict["parameterization"]
        )

        self._get_unit_converted_parameters_and_data_dwf()

        self._setup_dwf()

    def _get_unit_converted_parameters_and_data_dwf(self) -> None:

        self.timestep = convert_units(
            self.component_config.time_parameters_units,
            INTERNAL_UNITS_TIME,
            self.timestep,
        )
        self.base_wastewater_flow = convert_units(
            self.component_config.flow_units,
            INTERNAL_UNITS_FLOW,
            self.component_config.base_wastewater_flow,
        )
        self.sin_t_shift_hours = convert_units(
            self.component_config.time_parameters_units,
            INTERNAL_UNITS_TIME,
            self.component_config.sin_t_shift_hours,
        )
        self.sin_amplitude_fraction = (
            self.component_config.sin_amplitude_fraction
        )

    def _setup_dwf(self) -> None:
        """for base wastewater flow, set flow as simple sin wave with 24-hour period"""
        t = np.arange(self.num_timesteps_input_data) * self.timestep
        sine_amplitude = (
            self.base_wastewater_flow * self.sin_amplitude_fraction
        )
        sine_shape = np.sin((t - self.sin_t_shift_hours) * (2 * np.pi / 24))
        # TODO: set sin_shape based on timestamp rather than index so that it will carryover
        #      to new dataset if initial time of day or timestep changes
        self.flow = self.base_wastewater_flow + sine_shape * sine_amplitude

    def run(
        self,
        starting_timestep: int = 1,
        # TODO: set up initial_conditions as pydantic to enforce constraints on values
        initial_conditions: Dict[str, float] = None,
        num_timesteps_to_run: int = None,
    ) -> None:
        """
        All component simulators must have a run() class taking the args above.
        This is the core simulation call after the component has been initialized.
        For DWF, flow calculated as preprocessing in _setup_component(), so nothing else needed in run()

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

        pass
