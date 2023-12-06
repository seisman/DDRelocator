"""
Main functions for relocation.
"""
import numpy as np
from ddrelocator.headers import Solution
from ddrelocator.helpers import distaz
from scipy import optimize


def try_solution(master, obslist, sol, keep_residual=False):
    """
    Calculate the RMS of traveltime residuals for a given solution.

    Parameters
    ----------
    obslist : list
        List of Obs objects.
    sol : Solution
        The solution to be tested.
    keep_residual : bool, optional
        If True, keep the dt_pre and residual in the Obs object.
    """
    # Convert the solution to absolute location
    latitude = master.latitude + sol.dlat
    longitude = master.longitude + sol.dlon
    # For all observations, calculate predicted traveltime difference and residual
    for obs in obslist:
        distance = distaz(latitude, longitude, obs.latitude, obs.longitude)[0]
        obs.dt_pre = obs.dtdd * (distance - obs.distance) + obs.dtdh * sol.ddepth
        obs.residual = obs.dt - obs.dt_pre

    # Calculate the RMS of residuals
    residuals = np.array([obs.residual for obs in obslist])
    weights = np.array([obs.weight for obs in obslist])
    # tmean is the weighted average of residuals, as the origin time correction
    sol.tmean = np.average(residuals, weights=weights)
    sol.misfit = np.sqrt(np.average((residuals - sol.tmean) ** 2.0, weights=weights))

    # keep dt_pre and residual in the obs object or not
    if keep_residual:
        for obs in obslist:
            obs.residual -= sol.tmean
    else:
        for obs in obslist:
            del obs.residual, obs.dt_pre


def try_solution_wrapper(params, *args):
    """
    Wrapper for try_solution() to be used in grid search.

    Parameters
    ----------
    params : tuple
        Tuple of parameters to be tested. Each element is a slice object.
    args : tuple
        (master, obslist)

    Returns
    -------
    misfit : float
        RMS of traveltime residuals.
    """
    dlat, dlon, ddep = params
    master, obslist = args
    sol = Solution(dlat, dlon, ddep)
    try_solution(master, obslist, sol)
    return sol.misfit


def find_solution(master, obslist, ranges, ncores=-1):
    """
    Find the best solution.

    Parameters
    ----------
    master : Event
        Master event.
    obslist : list
        List of Obs objects.
    ranges : tuple
        Tuple of slice objects for grid search.
    ncores : int, optional
        Number of cores to use. If -1, use all available cores.

    Returns
    -------
    tuple
        The best solution, and the grid/Jout from scipy.optimize.brute function.
    """
    result = optimize.brute(
        func=try_solution_wrapper,
        ranges=ranges,
        args=(master, obslist),
        finish=None,
        full_output=True,
        workers=ncores,
    )
    dlat, dlon, ddep = result[0]
    grid, Jout = result[2], result[3]
    return Solution(dlat, dlon, ddep), grid, Jout
