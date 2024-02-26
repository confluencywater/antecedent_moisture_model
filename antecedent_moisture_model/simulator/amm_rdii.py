from typing import Dict

import numpy as np
from pydantic import PositiveFloat

from .amm_baseflow import AMMBaseflowConfig, AMMBaseflowSimulator
from .calculations import (
    get_moving_avg_backward,
    get_vectorized_difference_equation_simulation,
)
from ..datatypes.units import (
    convert_units,
    INTERNAL_UNITS_TIME,
    INTERNAL_UNITS_PRECIP,
)


class AMMRDIIConfig(AMMBaseflowConfig):
    antecedent_moisture_half_life_time: PositiveFloat = 7.0


class AMMRDIISimulator(AMMBaseflowSimulator):
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

        self.component_config_dict = component_config_dict

        self.num_timesteps_input_data = len(precip)

        self.component_config = AMMRDIIConfig(
            **component_config_dict["parameterization"]
        )

        self._get_unit_converted_parameters_baseflow()

        self._get_unit_converted_parameters_additional_rdii()

        self._setup_amm_baseflow()

        self._setup_additional_rdii()

    def _get_unit_converted_parameters_additional_rdii(
        self,
    ) -> None:
        self.antecedent_moisture_half_life_time = convert_units(
            self.component_config.time_parameter_units,
            INTERNAL_UNITS_TIME,
            self.component_config.antecedent_moisture_half_life_time,
        )

    def _setup_additional_rdii(self) -> None:
        """
        Additional setup for variables needed by
        rdii components but not baseflow
        """
        self.addl_capture_fraction = np.zeros(self.num_timesteps_input_data)
        self.antecedent_moisture_retention_factor = 0.5 ** (
            self.timestep / self.antecedent_moisture_half_life_time
        )

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
        self._simulate_amm_rdii(starting_timestep, num_timesteps_to_run)

    def _simulate_amm_rdii(
        self,
        starting_timestep: int,
        num_timesteps_to_run: int,
    ) -> None:

        end_timestep = starting_timestep + num_timesteps_to_run

        # capture fraction: if not baseflow model, use full calculation that depends on antecedent moisture.
        # NOTE: I don't know why we need to do scaling conversion for SHCF, not clear from equations.
        #       It seems that equations are written for precip in inches, and SHCF must not be scale free.
        #       Actually baseflow doesnt need this, so seems like addl capture fraction has inches embedded somehow?
        addl_capture_fraction_additive_component = (
            (self.antecedent_moisture_retention_factor - 1)
            / np.log(self.antecedent_moisture_retention_factor)
            * self.seasonal_hydro_condition_factor[
                starting_timestep:end_timestep
            ]
            * convert_units(INTERNAL_UNITS_PRECIP, "INCHES", 1)
            * self.moving_avg_precip[starting_timestep:end_timestep]
        )
        self.addl_capture_fraction[starting_timestep:end_timestep] = (
            np.maximum(
                get_vectorized_difference_equation_simulation(
                    additive_component=addl_capture_fraction_additive_component,
                    multiplier_for_simulated_variable_tminus1=self.antecedent_moisture_retention_factor,
                    simulated_variable_t0=self.addl_capture_fraction[
                        starting_timestep - 1
                    ],
                ),
                0.0,
            )
        )

        movavg2_start = starting_timestep - 1
        movavg2_end = starting_timestep + num_timesteps_to_run
        addl_capture_fraction_movavg2 = get_moving_avg_backward(
            self.addl_capture_fraction[movavg2_start:movavg2_end],
            2,
            0,
        )
        self.total_capture_fraction[starting_timestep:end_timestep] = (
            np.minimum(
                self.dry_weather_capture_fraction
                + addl_capture_fraction_movavg2[1:],
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
