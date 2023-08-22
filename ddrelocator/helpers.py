"""
Helper functions for ddrelocator.
"""
import warnings

import numpy as np
import pandas as pd
from ddrelocator.ddrelocator import Obs


def get_ttime_slowness(model, depth, distance, phase_list):
    """
    Get travel time, horizontal slowness, and vertical slowness for a given phase.

    Parameters
    ----------
    model : obspy.taup.TauPyModel
        TauPy model.
    depth : float
        Source depth in km.
    distance : float
        Epicentral distance in degree.
    phase_list : str
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
    The vertical slowness is defined as the negative of the vertical derivative of travel time.

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
    elif len(arrivals) > 1:
        warnings.warn(
            f"More than one arrivals found for depth={depth} and distance={distance}. "
            + "The first one is used."
        )

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
    with open(filename, "w") as f:
        f.write(
            "station latitude longitude distance azimuth phase time dtdd dtdh dt use\n"
        )
        for obs in obslist:
            f.write(
                f"{obs.station} {obs.latitude:.4f} {obs.longitude:.4f} "
                + f"{obs.distance:.4f} {obs.azimuth:.2f} "
                + f"{obs.phase} {obs.time:.4f} {obs.dtdd:.4f} {obs.dtdh:.4f} {obs.dt:.3f} "
                + f"{obs.use}\n"
            )


def read_obslist(filename):
    """
    Read list of observations from a file.

    Parameters
    ----------
    filename : str
        Input filename.
    """
    df = pd.read_csv(filename, delim_whitespace=True, comment="#")
    obslist = []
    for _, row in df.iterrows():
        obslist.append(
            Obs(
                row["station"],
                row["latitude"],
                row["longitude"],
                row["distance"],
                row["azimuth"],
                row["phase"],
                row["time"],
                row["dtdd"],
                row["dtdh"],
                row["dt"],
                row["use"],
            )
        )
    return obslist
