import numpy as np
from scipy.signal import lfilter


def get_moving_avg_backward(
    a: np.ndarray, moving_avg_steps: int, backward_offset: int = 1
):
    """
    get backward looking moving average (see https://stackoverflow.com/questions/14313510/how-to-calculate-rolling-moving-average-using-python-numpy-scipy)
    Args:
        a: np.ndarray
        moving_avg_steps: window to get moving average over
        backward_offset: number of steps behind to look

    Example:
        a = array([1, 4, 5, 8, 3])
        get_moving_avg_backward(a, 2,0) = array([0. , 2.5, 4.5, 6.5, 5.5])
        get_moving_avg_backward(a, 2,1) = array([0. , 0. , 2.5, 4.5, 6.5])
    """
    assert moving_avg_steps < len(a)
    a_movavg = np.zeros(len(a))
    convolution = (
        np.convolve(a, np.ones(moving_avg_steps), "valid") / moving_avg_steps
    )
    if backward_offset > 0:
        a_movavg[moving_avg_steps - 1 + backward_offset :] = convolution[
            :-(backward_offset)
        ]
    else:
        a_movavg[moving_avg_steps - 1 :] = convolution
    return a_movavg


def get_vectorized_difference_equation_simulation(
    additive_component: np.ndarray,
    multiplier_for_simulated_variable_tminus1: float,
    simulated_variable_t0: float,
):
    """
    Function for vectorizing simulation of a variable defined by 1st order difference equation using digital filter.
    See https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html

    simulated_variable[t] = additive_component[t] + (multiplier_for_simulated_variable_tminus1 * simulated_variable[t-1])
    initial_condition: simulated_variable[t=0] = simulated_variable_t0
    """
    simulated_variable, _ = lfilter(
        b=[1, 0],
        a=[1, -multiplier_for_simulated_variable_tminus1],
        x=additive_component,
        zi=[simulated_variable_t0],
    )
    return simulated_variable
