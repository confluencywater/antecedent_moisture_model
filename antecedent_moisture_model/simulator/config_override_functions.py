from typing import Dict, List


def override_components_to_include(
    components_to_include_override: List[str], simulation_config_dict: Dict
) -> List[str]:
    """
    Function to override default set of components from simulation config file.
    This can be useful for interactive mode.

    Args:
        components_to_include_override (List[str]): list of components to include
        simulation_config_dict: dict with simulation config

    Returns:
        dict: updated version of simulation_config_dict with updated components

    """
    if components_to_include_override is not None:
        assert all(
            [
                c in simulation_config_dict["components_to_use"]
                for c in components_to_include_override
            ]
        )
        component_labels = components_to_include_override
    else:
        component_labels = simulation_config_dict["components_to_use"]
    return component_labels


def override_component_params(
    component_label: str,
    component_param_config_dict: Dict[str, float],
    params_to_override_labels: List[str],
    params_to_override_values: List[str],
) -> Dict[str, float]:
    """
    Function to override default parameters in simulation config file.
    This can be useful for calibration.

    Args:
        component_label (str): label of the component in the simulation config file
        component_param_config_dict: default parameterization for param from config
        params_to_override_labels (List[str]): list of parameters to override
        params_to_override_values (List[float]): new values for the parameters

    Returns:
        dict: updated version of component_param_config_dict with updated param values
    """
    if (
        params_to_override_labels is not None
        and params_to_override_values is not None
    ):
        for k, v in zip(
            params_to_override_labels,
            params_to_override_values,
        ):
            prefix = component_label
            if prefix in k:
                component_param_config_dict["parameterization"][
                    k.replace(f"{prefix}_", "")
                ] = v
    return component_param_config_dict
