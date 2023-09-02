"""
Main functions for relocation.
"""
import itertools

import numpy as np
from ddrelocator.headers import Solution
from ddrelocator.helpers import distaz


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


def gridsearch(master, obslist, params):
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

    Returns
    -------
    solutions : list
        List of Solution objects.
    """
    solutions = []
    for ddep, dlat, dlon in itertools.product(params.ddeps, params.dlats, params.dlons):
        sol = Solution(dlat, dlon, ddep, master)
        try_solution(obslist, sol)
        solutions.append(sol)
    return solutions


def find_best_solution(solutions):
    """
    Find the best solution.

    Parameters
    ----------
    solutions : list
        List of Solution objects.

    Returns
    -------
    best : Solution
        Best Solution object.
    """
    idx = np.argmin([i.misfit for i in solutions])
    return solutions[idx]
