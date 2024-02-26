from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd

from ..datatypes.units import (
    INTERNAL_UNITS_PRECIP,
    INTERNAL_UNITS_TEMPERATURE,
    INTERNAL_UNITS_FLOW,
)
from ..simulator.dwf import DWFSimulator


def export_to_csv(
    component_labels: List[str],
    input_data: Dict[str, np.ndarray],
    amm_components: List,
    flow: np.ndarray,
    filename_path: Path,
) -> None:
    results_dict = {}
    results_dict[f"precip_{INTERNAL_UNITS_PRECIP}"] = input_data["precip"]
    results_dict[f"temperature_{INTERNAL_UNITS_TEMPERATURE}"] = input_data[
        "temperature"
    ]
    if "flow" in input_data:
        results_dict[f"observed_flow_{INTERNAL_UNITS_FLOW}"] = input_data[
            "flow"
        ]
    for component, component_label in zip(amm_components, component_labels):
        if not isinstance(component, DWFSimulator):
            results_dict[f"{component_label}_total_capture_fraction"] = (
                component.total_capture_fraction
            )
        results_dict[f"{component_label}_flow_{INTERNAL_UNITS_FLOW}"] = (
            component.flow
        )
    results_dict[f"total_flow_{INTERNAL_UNITS_FLOW}"] = flow
    results_df = pd.DataFrame(results_dict, index=input_data["timestamp"])
    results_df.to_csv(filename_path)
