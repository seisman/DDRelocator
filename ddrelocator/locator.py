"""
Main functions for relocation.
"""
import numpy as np
from ddrelocator.headers import Solution
from ddrelocator.helpers import distaz
from scipy import optimize


def try_solution(obslist, sol, keep_residual=False):
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
    # For all observations, calculate predicted traveltime difference and residual
    for obs in obslist:
        distance = distaz(sol.latitude, sol.longitude, obs.latitude, obs.longitude)[0]
        obs.dt_pre = obs.dtdd * (distance - obs.distance) + obs.dtdh * sol.ddepth
        obs.residual = obs.dt - obs.dt_pre

    # Only observations with use=True are used to calculate the mean and RMS.
    residuals = np.array([obs.residual for obs in obslist if obs.use])
    # tmean is taken as the origin time correction
    sol.tmean = residuals.mean()
    sol.misfit = np.sqrt(np.mean((residuals - sol.tmean) ** 2.0))

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
    sol = Solution(dlat, dlon, ddep, master)
    try_solution(obslist, sol)
    return sol.misfit


def gridsearch(master, obslist, params, ncores=-1):
    """
    Grid search all possible solutions.

    Parameters
    ----------
    master : Event
        Master event.
    obslist : list
        List of Obs objects.
    params : SearchParams
        Search parameters.
    ncores : int, optional
        Number of cores to use. If -1, use all available cores.

    Returns
    -------
    solutions : list
        List of Solution objects.
    """
    result = optimize.brute(
        func=try_solution_wrapper,
        ranges=(params.dlats, params.dlons, params.ddeps),
        args=(master, obslist),
        finish=None,
        full_output=True,
        workers=ncores,
    )
    dlat, dlon, ddep = result[0]
    grid, Jout = result[2], result[3]
    return Solution(dlat, dlon, ddep, master), grid, Jout
