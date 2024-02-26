from typing import Dict

import numpy as np
import pandas as pd

from .datamodel import InputDataConfig
from ..datatypes.units import (
    convert_units,
    INTERNAL_UNITS_PRECIP,
    INTERNAL_UNITS_TEMPERATURE,
    INTERNAL_UNITS_FLOW,
)
from .exceptions import (
    InvalidOrMissingTimestampException,
    MissingDataColumnException,
)

VARNAMES_WEATHER = ["precip", "temperature"]
VARNAMES_FLOW = ["flow"]
VARNAMES_INTERMEDIATE = [
    "moving_avg_precip",
    "moving_avg_temperature",
    "seasonal_hydro_condition_factor",
    "addl_capture_fraction",
    "total_capture_fraction",
]


class TimeseriesSetup:
    def __init__(
        self,
        input_data: pd.DataFrame,
        input_data_config: InputDataConfig,
        timestep: float = None,
    ) -> None:
        self.input_data = input_data
        self.config = input_data_config
        self.timestep = timestep
        self.num_timesteps_input_data = self.input_data.shape[0]

    def run(self) -> Dict[str, np.ndarray]:
        timeseries_dict = {}

        self._verify_timestamp()
        timeseries_dict["timestamp"] = self._get_timestamp()

        varnames = VARNAMES_WEATHER
        if self.config.has_flow_data:
            varnames += VARNAMES_FLOW
        if self.config.has_intermediate_data:
            varnames += VARNAMES_INTERMEDIATE

        for var in varnames:
            timeseries_dict[var] = self._get_single_timeseries(var)

        return timeseries_dict

    def _verify_timestamp(self) -> pd.DatetimeIndex:
        if not isinstance(
            self.input_data[self.config.timestamp_colname].iloc[0], str
        ):
            raise InvalidOrMissingTimestampException
        self.input_data.index = pd.DatetimeIndex(
            self.input_data[self.config.timestamp_colname]
        )

        min_timestep = np.diff(self.input_data.index.values).min().astype(int)
        max_timestep = np.diff(self.input_data.index.values).max().astype(int)
        if not np.abs(min_timestep / max_timestep - 1) < 0.01:
            raise InvalidOrMissingTimestampException

        if self.timestep is not None:
            timestep_hours = max_timestep / (60 * 60 * 1e9)
            if not timestep_hours - self.timestep < 1e-3:
                raise InvalidOrMissingTimestampException

    def _get_timestamp(self) -> pd.DatetimeIndex:
        return self.input_data.index

    def _get_single_timeseries(self, var: str) -> pd.Series:
        try:
            timeseries = self.input_data[
                self.config.__getattribute__(f"{var}_colname")
            ]
        except KeyError:
            raise MissingDataColumnException(
                f'column for {var} ({self.config.__getattribute__(f"{var}_colname")}) not found'
            )

        timeseries = self._clean_timeseries(timeseries)
        timeseries = self._convert_to_internal_units(var, timeseries)
        return timeseries

    def _clean_timeseries(self, timeseries: pd.Series) -> np.ndarray:
        timeseries = timeseries.astype(float)

        timeseries = timeseries.to_numpy()

        # set NANs to 0, following AMM spreadsheet Tab 20, since that is how Excel treats NANs for formulas
        # TODO after verification: might be better to take an incomplete averaging or something instead of using zero?
        timeseries = np.nan_to_num(timeseries, nan=0.0, copy=True)

        return timeseries

    def _convert_to_internal_units(self, var: str, timeseries: np.ndarray):
        """
        Convert timeseries to the following units for internal calculations:

        precip: FEET (depth within timestep, rather than a rate)
        temperature: FAHRENHEIT
        flow: CUBICFEETPERSECOND
        catchment area: SQUAREFEET
        """
        if "precip" in var:
            timeseries = convert_units(
                self.config.precip_units, INTERNAL_UNITS_PRECIP, timeseries
            )
        elif "temperature" in var:
            timeseries = convert_units(
                self.config.temperature_units,
                INTERNAL_UNITS_TEMPERATURE,
                timeseries,
            )
        elif "flow" in var:
            timeseries = convert_units(
                self.config.flow_units, INTERNAL_UNITS_FLOW, timeseries
            )
        return timeseries


def setup_timeseries(
    input_data: pd.DataFrame,
    input_data_config: InputDataConfig,
    timestep_hours: int = None,
):
    """
    Function for preparing input data for use with AMM model

    Args:
        input_data: pandas DataFrame
            index: pandas DateTimeIndex, with name given by timestamp_colname in input_data_config
            columns:
                Must include precip & temperature (with column names given in config).
                Must include flow if has_flow_data==True in config
                Must include intermediate variables if has_intermediate_data==True in config.
                See InputDataConfig definition for more details.
        input_data_config: InputDataConfig object
        timestep_hours (int): model timestep. Curretnly must be equal to data timestep, but this isn't necessary constraint.

    Return:
        Dict:
            "timestamp": pd.DateTimeIndex
            "precip": np.ndarray
            "temperature": np.ndarray
            if has_flow_data or has_intermediate_data, these will be included as well.

    """
    return TimeseriesSetup(input_data, input_data_config, timestep_hours).run()
