INTERNAL_UNITS_TIME = "SECONDS"
INTERNAL_UNITS_PRECIP = "FEET"
INTERNAL_UNITS_TEMPERATURE = "FAHRENHEIT"
INTERNAL_UNITS_AREA = "SQUAREFEET"
INTERNAL_UNITS_FLOW = "CUBICFEETPERSECOND"

unit_conversions_dict = {
    "precip": {
        "FEET_TO_INCHES": 12,
        "FEET_TO_CENTIMETERS": 12 * 2.54,
        "INCHES_TO_CENTIMETERS": 2.54,
    },
    "flow": {
        "CUBICMETERSPERSECOND_TO_CUBICFEETPERSECOND": 35.31466621266132,
        "GALLONSPERSECOND_TO_CUBICFEETPERSECOND": 0.13368056,
        "LITERSPERSECOND_TO_CUBICFEETPERSECOND": 0.03531467,
        "MILLIONGALLONSPERDAY_TO_CUBICFEETPERSECOND": 1.5472286365101,
    },
    "area": {
        "ACRES_TO_SQUAREFEET": 43560,
        "SQUAREMETERS_TO_SQUAREFEET": 10.7639104,
        "SQUAREMILES_TO_SQUAREFEET": 27878400,
        "SQUAREKILOMETERS_TO_SQUAREFEET": 10763910.41670972,
        "HECTARES_TO_SQUAREFEET": 107639.104,
    },
    "time": {
        "DAYS_TO_HOURS": 24,
        "HOURS_TO_SECONDS": 3600,
        "DAYS_TO_SECONDS": 24 * 3600,
    },
}

units_options_dict = {
    "precip": [
        "INCHES",
        "FEET",
        "CENTIMETERS",
    ],
    # NOTE: Rates not implemented (eg INCHESPERHOUR). Would need to account for timestep.
    "temperature": ["FAHRENHEIT", "CELSIUS"],
    "flow": [
        "CUBICMETERSPERSECOND",
        "CUBICFEETPERSECOND",
        "GALLONSPERSECOND",
        "LITERSPERSECOND",
        "MILLIONGALLONSPERDAY",
    ],
    "area": [
        "SQUAREFEET",
        "SQUAREMETERS",
        "SQUAREMILES",
        "SQUAREKILOMETERS",
        "ACRES",
        "HECTARES",
    ],
    "time": ["SECONDS", "HOURS", "DAYS"],
}


def convert_units(starting_units, ending_units, starting_value):

    if starting_units == ending_units:
        return starting_value

    for units_type, units_type_dict in units_options_dict.items():
        if starting_units in units_type_dict:
            break
    assert ending_units in units_type_dict

    if starting_units == "FAHRENHEIT" and ending_units == "CELSIUS":
        return (starting_value - 32) / 1.8
    elif starting_units == "CELSIUS" and ending_units == "FAHRENHEIT":
        return 1.8 * starting_value + 32

    elif (
        f"{starting_units}_TO_{ending_units}"
        in unit_conversions_dict[units_type]
    ):
        multiplier = unit_conversions_dict[units_type][
            f"{starting_units}_TO_{ending_units}"
        ]
    elif (
        f"{ending_units}_TO_{starting_units}"
        in unit_conversions_dict[units_type]
    ):
        multiplier = (
            1
            / unit_conversions_dict[units_type][
                f"{ending_units}_TO_{starting_units}"
            ]
        )
    else:
        raise NotImplementedError

    return starting_value * multiplier
