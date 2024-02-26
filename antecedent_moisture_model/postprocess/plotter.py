from pathlib import Path
from typing import List, Dict

import matplotlib.pyplot as plt
import numpy as np

from ..simulator.dwf import DWFSimulator


def plot_simulated_results(
    component_labels: List[str],
    input_data: Dict[str, np.ndarray],
    amm_components: List,
    flow: np.ndarray,
    figure_path: Path,
    zoom_indices: List[int] = None,
):
    fig, axs = plt.subplots(3, 1, figsize=(6, 8))
    colors = ["k", "0.5", "goldenrod", "firebrick", "cornflowerblue"]
    flow_labels = ["observed", "amm total"]
    ax = axs[0]
    ax.plot(
        input_data["timestamp"],
        input_data["precip"],
        color=colors[0],
    )
    ax.set_ylabel("Precipitation (in)")
    ax = axs[1]
    for ic, component in enumerate(amm_components):
        if not isinstance(component, DWFSimulator):
            ax.plot(
                input_data["timestamp"],
                component.total_capture_fraction,
                color=colors[ic + 2],
                label=component_labels[ic],
            )
    ax.set_ylabel("Total capture fraction")
    ax.legend()
    ax = axs[2]
    ax.plot(
        input_data["timestamp"],
        input_data["flow"],
        color=colors[0],
        label=flow_labels[0],
        zorder=1,
    )
    ax.plot(
        input_data["timestamp"],
        flow,
        color=colors[1],
        label=flow_labels[1],
        zorder=1,
    )
    for ic, component in enumerate(amm_components):
        ax.plot(
            input_data["timestamp"],
            component.flow,
            color=colors[ic + 2],
            label=component_labels[ic],
            alpha=0.8,
            zorder=2,
        )

    if zoom_indices is not None:
        for ax in axs:
            ax.set_xlim(
                [
                    input_data["timestamp"][zoom_indices[0]],
                    input_data["timestamp"][zoom_indices[1]],
                ]
            )

    ax.legend()
    ax.set_ylabel("Flow (cfs)")
    plt.savefig(figure_path, bbox_inches="tight", dpi=300)
