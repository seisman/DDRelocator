"""
Main functions for relocation.
"""
import numpy as np
from ddrelocator.headers import Solution
from ddrelocator.helpers import distaz
from obspy.geodetics import kilometers2degrees
from scipy import optimize


def try_solution(master, obslist, sol, keep_residual=False):
    """
    Calculate the RMS of traveltime residuals for a given solution.

    Parameters
    ----------
    master : Event
        Master event.
    obslist : list
        List of Obs objects.
    sol : Solution
        The solution to be tested.
    keep_residual : bool, optional
        If True, keep the dt_pre and residual in the Obs object.
    """
    if sol.type == "geographic":
        # Convert the solution to absolute location
        latitude = master.latitude + sol.dlat
        longitude = master.longitude + sol.dlon
        # For all observations, calculate distance differentce and traveltime difference
        for obs in obslist:
            distance = distaz(latitude, longitude, obs.latitude, obs.longitude)[0]
            obs.dt_pre = obs.dtdd * (distance - obs.distance) + obs.dtdh * sol.ddepth
    elif sol.type == "cylindrical":
        ddist = sol.ddist / 1000.0  # convert to km
        ddepth = sol.ddepth / 1000.0  # convert to km
        for obs in obslist:
            obs.dt_pre = (
                obs.dtdd
                * kilometers2degrees(-ddist * np.cos(np.radians(sol.az - obs.azimuth)))
                + obs.dtdh * ddepth
            )

    # Calculate the residuals
    for obs in obslist:
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
        Parameters for brute force search. It's also the parameters
        for the solution to be tested.
    args : tuple
        Tuple of (master, obslist, sol_type).

    Returns
    -------
    misfit : float
        RMS of traveltime residuals.
    """
    master, obslist, sol_type = args
    sol = Solution(params, sol_type)
    try_solution(master, obslist, sol)
    return sol.misfit


def find_solution(master, obslist, ranges, sol_type, ncores=-1):
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
    sol_type : str
        Solution type, either 'geographic' or 'cylindrical'.
    ncores : int, optional
        Number of cores to use. If -1, use all available cores.

    Returns
    -------
    tuple
        The best solution, and the grid/Jout from scipy.optimize.brute function.
    """
    if sol_type not in ["geographic", "cylindrical"]:
        raise ValueError(f"Unrecognized solution type '{sol_type}'.")
    result = optimize.brute(
        func=try_solution_wrapper,
        ranges=ranges,
        args=(master, obslist, sol_type),
        finish=None,
        full_output=True,
        workers=ncores,
    )
    params, _, grid, Jout = result
    return Solution(params, sol_type), grid, Jout
