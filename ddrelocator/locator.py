"""
DDRelocator

Determine the relative location of two nearby events using the master-event algorithm.
"""
import itertools

import numpy as np
from ddrelocator.headers import Solution
from ddrelocator.helpers import distaz


def try_solution(obslist, sol):
    """
    Calculate the RMS of traveltime residuals for a given solution.

    Parameters
    ----------
    obslist : list
        List of Obs objects.
    sol : Solution
        The solution to be tested.
    """
    # loop over all observations and calculate the predicted travel time difference
    # and traveltime difference residual
    for obs in obslist:
        distance = distaz(sol.latitude, sol.longitude, obs.latitude, obs.longitude)[0]
        obs.dt_pre = obs.dtdd * (distance - obs.distance) + obs.dtdh * sol.ddepth
        obs.residual = obs.dt - obs.dt_pre

    # only use the observations with use=1 when calculating the mean and RMS.
    obslist_use = [obs for obs in obslist if obs.use == 1]
    sol.tmean = np.mean([obs.residual for obs in obslist_use])

    # tmean is regarded as the origin time correction. so remove it from all residuals.
    for obs in obslist:
        obs.residual -= sol.tmean

    # determine the RMS misfit of the residuals
    sol.misfit = np.sqrt(np.mean([obs.residual**2.0 for obs in obslist_use]))


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
