from typing import Dict

import numpy as np
from pydantic import BaseModel, PositiveFloat, confloat, field_validator

from .calculations import (
    get_moving_avg_backward,
    get_vectorized_difference_equation_simulation,
)
from ..datatypes.units import (
    convert_units,
    units_options_dict,
    INTERNAL_UNITS_TIME,
    INTERNAL_UNITS_AREA,
    INTERNAL_UNITS_TEMPERATURE,
)


class AMMBaseflowConfig(BaseModel):
    catchment_area: PositiveFloat
    catchment_area_units: str = "ACRES"
    hydrograph_half_life_time: PositiveFloat = 12.0
    time_parameter_units: str = "HOURS"
    dry_weather_capture_fraction: confloat(ge=0.0, le=1.0) = 0.03
    precip_averaging_time: PositiveFloat = 1.0
    temperature_averaging_time: PositiveFloat = 720.0
    cold_temperature: float = 30.0
    temperature_parameter_units: str = "FAHRENHEIT"
    addl_capture_fraction_cold: confloat(ge=0.0, le=1.0) = 0.05
    hot_temperature: float = 70.0
    addl_capture_fraction_hot: confloat(ge=0.0, le=1.0) = 0.01
    flow_units: str = "CUBICFEETPERSECOND"

    @property
    def cold_temperature_corrected(self) -> float:
        return min(self.cold_temperature, self.hot_temperature)

    @property
    def hot_temperature_corrected(self) -> float:
        return max(self.cold_temperature, self.hot_temperature)

    @field_validator("catchment_area_units")
    def validate_catchment_area_units(cls, v):
        assert v in units_options_dict["area"]
        return v

    @field_validator("temperature_parameter_units")
    def validate_temperature_parameter_units(cls, v):
        assert v in units_options_dict["temperature"]
        return v

    @field_validator("time_parameter_units")
    def validate_time_parameter_units(cls, v):
        assert v in units_options_dict["time"]
        return v

    @field_validator("flow_units")
    def validate_flow_units(cls, v):
        assert v in units_options_dict["flow"]
        return v


class AMMBaseflowSimulator:
    def __init__(
        self,
        component_config_dict: Dict,
        precip: np.ndarray,
        temperature: np.ndarray,
        timestep: float,
    ) -> None:

        self.precip = precip
        self.temperature = temperature
        self.timestep = timestep

        self.num_timesteps_input_data = len(precip)

        self.component_config = AMMBaseflowConfig(
            **component_config_dict["parameterization"]
        )

        self._get_unit_converted_parameters_baseflow()

        self._setup_amm_baseflow()

    def _get_unit_converted_parameters_baseflow(self) -> None:

        self.catchment_area = convert_units(
            self.component_config.catchment_area_units,
            INTERNAL_UNITS_AREA,
            self.component_config.catchment_area,
        )
        self.hydrograph_half_life_time = convert_units(
            self.component_config.time_parameter_units,
            INTERNAL_UNITS_TIME,
            self.component_config.hydrograph_half_life_time,
        )
        self.precip_averaging_time = convert_units(
            self.component_config.time_parameter_units,
            INTERNAL_UNITS_TIME,
            self.component_config.precip_averaging_time,
        )
        self.temperature_averaging_time = convert_units(
            self.component_config.time_parameter_units,
            INTERNAL_UNITS_TIME,
            self.component_config.temperature_averaging_time,
        )
        self.cold_temperature = convert_units(
            self.component_config.temperature_parameter_units,
            INTERNAL_UNITS_TEMPERATURE,
            self.component_config.cold_temperature_corrected,
        )
        self.hot_temperature = convert_units(
            self.component_config.temperature_parameter_units,
            INTERNAL_UNITS_TEMPERATURE,
            self.component_config.hot_temperature_corrected,
        )
        self.dry_weather_capture_fraction = (
            self.component_config.dry_weather_capture_fraction
        )
        self.addl_capture_fraction_cold = (
            self.component_config.addl_capture_fraction_cold
        )
        self.addl_capture_fraction_hot = (
            self.component_config.addl_capture_fraction_hot
        )

    def _setup_amm_baseflow(self) -> None:
        """
        This precomputes all parameters, moving averages, etc,
        that are not part of core simulation
        """
        self.shape_factor = 0.5 ** (
            self.timestep / self.hydrograph_half_life_time
        )
        self.moving_avg_steps_precip = (
            int(self.precip_averaging_time / self.timestep) + 1
        )
        self.moving_avg_steps_temperature = (
            int(self.temperature_averaging_time / self.timestep) + 1
        )
        self.time_to_peak = self.precip_averaging_time + self.timestep
        self.sigmoid_max = 1.2 * (
            self.addl_capture_fraction_cold - self.addl_capture_fraction_hot
        )
        self.sigmoid_steepness = 4.7964 / (
            self.cold_temperature - self.hot_temperature
        )
        self.sigmoid_midpoint = (
            self.cold_temperature + self.hot_temperature
        ) / 2

        self.moving_avg_precip = get_moving_avg_backward(
            self.precip, self.moving_avg_steps_precip
        )
        self.moving_avg_temperature = get_moving_avg_backward(
            self.temperature, self.moving_avg_steps_temperature
        )
        self.seasonal_hydro_condition_factor = (
            self.sigmoid_max
            / (
                1
                + np.exp(
                    -self.sigmoid_steepness
                    * (self.moving_avg_temperature - self.sigmoid_midpoint)
                )
            )
            + self.addl_capture_fraction_cold
            - (11 / 12) * self.sigmoid_max
        )
        self.seasonal_hydro_condition_factor = np.maximum(
            self.seasonal_hydro_condition_factor, 0
        )

        self.total_capture_fraction = np.zeros(self.num_timesteps_input_data)
        self.flow = np.zeros(self.num_timesteps_input_data)

    def run(
        self,
        starting_timestep: int = 1,
        # TODO: set up initial_conditions as pydantic to enforce constraints on values
        initial_conditions: Dict[str, float] = None,
        num_timesteps_to_run: int = None,
    ) -> None:
        """
        This is the core simulation call after the component has been initialized.
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
        if num_timesteps_to_run == 0:
            return

        # start simulation at t>=1 due to recursive equations.
        assert starting_timestep > 0

        if num_timesteps_to_run is None:
            num_timesteps_to_run = self.num_timesteps_input_data - 1
        assert (
            starting_timestep + num_timesteps_to_run
            <= self.num_timesteps_input_data
        )

        self._set_initial_conditions(starting_timestep, initial_conditions)
        self._simulate_amm_baseflow(starting_timestep, num_timesteps_to_run)

    def _set_initial_conditions(
        self, starting_timestep: int, initial_conditions: Dict
    ) -> None:
        """
        Set initial conditions

        Args:
            starting_timestep (int): index/timestep to start simulation
            initial_conditions: Dict
                total_capture_fraction (float): value of total_capture_fraction on timestep = (starting_timestep - 1)
                flow (float): value of flow on timestep = (starting_timestep - 1)
        """
        if initial_conditions is None:
            # if initial conditions aren't given, total capture fraction & flow will have initialized values of zero
            pass
        else:
            self.total_capture_fraction[starting_timestep - 1] = max(
                initial_conditions["total_capture_fraction"], 0.0
            )
            self.flow[starting_timestep - 1] = max(
                initial_conditions["flow"], 0.0
            )

    def _simulate_amm_baseflow(
        self,
        starting_timestep: int,
        num_timesteps_to_run: int,
    ) -> None:
        # total capture fraction (RW_t): for baseflow this uses SHCF directly instead of additional_capture_fraction
        movavg2_start = starting_timestep - 1
        movavg2_end = starting_timestep + num_timesteps_to_run
        seasonal_hydro_condition_factor_movavg2 = get_moving_avg_backward(
            self.seasonal_hydro_condition_factor[movavg2_start:movavg2_end],
            2,
            0,
        )
        end_timestep = starting_timestep + num_timesteps_to_run
        self.total_capture_fraction[starting_timestep:end_timestep] = (
            np.minimum(
                np.maximum(
                    self.dry_weather_capture_fraction
                    + seasonal_hydro_condition_factor_movavg2[1:],
                    0.0,
                ),
                1.0,
            )
        )

        flow_additive_component = (
            (self.catchment_area)
            * (1 - self.shape_factor)
            / (self.timestep)
            * self.total_capture_fraction[starting_timestep:end_timestep]
            * self.moving_avg_precip[starting_timestep:end_timestep]
        )
        self.flow[starting_timestep:end_timestep] = np.maximum(
            get_vectorized_difference_equation_simulation(
                additive_component=flow_additive_component,
                multiplier_for_simulated_variable_tminus1=self.shape_factor,
                simulated_variable_t0=self.flow[starting_timestep - 1],
            ),
            0.0,
        )
