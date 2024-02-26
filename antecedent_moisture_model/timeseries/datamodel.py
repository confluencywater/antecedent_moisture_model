from pydantic import BaseModel, NonNegativeInt, field_validator

from ..datatypes.units import units_options_dict


class InputDataConfig(BaseModel):
    input_data_file: str = "input_data.csv"
    skip_rows: NonNegativeInt = 0
    timestamp_colname: str = "timestamp"
    precip_colname: str = "precip"
    precip_units: str = "INCHES"
    temperature_colname: str = "temperature"
    temperature_units: str = "FAHRENHEIT"
    has_flow_data: bool = False
    flow_colname: str = "flow"
    flow_units: str = "CUBICFEETPERSECOND"
    has_intermediate_data: bool = False
    moving_avg_precip_colname: str = None
    moving_avg_temperature_colname: str = None
    seasonal_hydro_condition_factor_colname: str = None
    addl_capture_fraction_colname: str = None
    total_capture_fraction_colname: str = None

    @field_validator("precip_units")
    def validate_precip_units(cls, v):
        assert v in units_options_dict["precip"]
        return v

    @field_validator("temperature_units")
    def validate_temperature_units(cls, v):
        assert v in units_options_dict["temperature"]
        return v

    @field_validator("flow_units")
    def validate_flow_units(cls, v):
        assert v in units_options_dict["flow"]
        return v
