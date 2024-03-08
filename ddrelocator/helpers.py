"""
Helper functions for ddrelocator.
"""

import pickle

import numpy as np
import pandas as pd
from ddrelocator.headers import Obs
from obspy.geodetics import gps2dist_azimuth, kilometers2degrees


def distaz(lat1, lon1, lat2, lon2):
    """
    Calculate distance (in degree) and azimuth between two geographic points.

    This function is a wrapper of obspy.geodetics.gps2dist_azimuth() and
    obspy.geodetics.kilometers2degrees().

    Parameters
    ----------
    lat1 : float
        Latitude of point 1 in degree.
    lon1 : float
        Longitude of point 1 in degree.
    lat2 : float
        Latitude of point 2 in degree.
    lon2 : float
        Longitude of point 2 in degree.

    Returns
    -------
    dist : float
        Distance between two points in degree.
    az : float
        Azimuth from point 1 to point 2 in degree.
    """
    dist, az, _ = gps2dist_azimuth(lat1, lon1, lat2, lon2)
    dist = kilometers2degrees(dist / 1000.0)
    return dist, az


def get_ttime_slowness(model, depth, distance, phase_list):
    """
    Get travel time, horizontal slowness, and vertical slowness for a given phase.

    If multiple phases are given or multiple arrivals are found, only the first one is
    used.

    Parameters
    ----------
    model : obspy.taup.TauPyModel
        TauPy model.
    depth : float
        Source depth in km.
    distance : float
        Epicentral distance in degree.
    phase_list : list of str
        List of phases.

    Returns
    -------
    phasename : str
        The actual phase name.
    time : float
        Travel time in second.
    dtdd : float
        Horizontal slowness in second/degree.
    dtdh : float
        Vertical slowness in second/km.

    Notes
    -----
    The vertical slowness is defined as the negative of the vertical derivative of
    travel time.
    """
    radius = 6371.0
    arrivals = model.get_travel_times(
        source_depth_in_km=depth,
        distance_in_degree=distance,
        phase_list=phase_list,
        receiver_depth_in_km=0.0,  # assuming receiver at surface
        ray_param_tol=1.0e-5,  # small tolerance to have better precision?
    )

    if len(arrivals) == 0:
        msg = f"No arrival found for depth={depth} and distance={distance}."
        raise ValueError(msg)

    # only use the first arrival
    arrival = arrivals[0]
    # phase name.
    phasename = arrival.name
    # travel time in sec.
    time = arrival.time
    # horizontal slowness in sec/degree.
    dtdd = arrival.ray_param_sec_degree
    # takeoff angle. zero for vertical down-going ray; 180 for vertical up-going ray.
    takeoff_angle = np.deg2rad(arrival.takeoff_angle)
    # vertical slowness.
    dtdh = -dtdd * 180.0 / np.pi / (radius - depth) / np.tan(takeoff_angle)
    return phasename, time, dtdd, dtdh


def obslist_to_dataframe(obslist):
    """
    Convert list of observations to pandas.DataFrame.

    Parameters
    ----------
    obslist : list
        List of Obs objects.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame of observations.
    """
    return pd.DataFrame([vars(obs) for obs in obslist])


def dump_obslist(obslist, filename):
    """
    Dump list of observations into a file.

    Parameters
    ----------
    obslist : list
        List of Obs objects.
    filename : str
        Output filename.
    """
    # Convert to pandas.DataFrame and save to CSV
    df = obslist_to_dataframe(obslist)
    df.to_csv(filename, sep=" ", index=False, float_format="%.6f")


def read_obslist(filename):
    """
    Read list of observations from a file.

    Parameters
    ----------
    filename : str
        Input filename.

    Returns
    -------
    obslist : list
        List of Obs objects.
    """
    df = pd.read_csv(filename, delim_whitespace=True, comment="#")
    return [Obs(*(df.values.tolist()[i])) for i in range(len(df.index))]


def dump_solutions(grid, Jout, filename):
    """
    Dump list of solutions into a file.
    """
    with open(filename, "wb") as f:
        pickle.dump((grid, Jout), f)


def load_solutions(filename):
    """
    Read list of solutions from a file.
    """
    with open(filename, "rb") as f:
        return pickle.load(f)
