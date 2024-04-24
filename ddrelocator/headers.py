"""
Classes for ddrelocator.
"""

from dataclasses import dataclass

import numpy as np
from obspy import UTCDateTime


@dataclass
class Event:
    """
    Class for event information.

    Parameters
    ----------
    origin
        Event origin time.
    latitude
        Event latitude.
    longitude
        Event longitude.
    depth
        Event depth in km.
    magnitude
        Event magnitude (unused).

    Attributes
    ----------
    id : str
        Event ID in the format of YYYYMMDDHHMMSS.
    """

    origin: str | UTCDateTime
    latitude: float
    longitude: float
    depth: float
    magnitude: float  # unused

    def __post_init__(self):
        self.origin = UTCDateTime(self.origin)
        self.id = self.origin.strftime("%Y%m%d%H%M%S")

    def __str__(self):
        return (
            f"{self.origin} {self.latitude:.5f} {self.longitude:.5f} {self.depth:.4f}"
        )


@dataclass
class Station:
    """
    Class for station information.

    Parameters
    ----------
    name
        Station name.
    latitude
        Station latitude.
    longitude
        Station longitude.
    elevation
        Station elevation (unused).
    """

    name: str
    latitude: float
    longitude: float
    elevation: float = 0.0  # unused


@dataclass
class Obs:
    """
    Class for observations.

    Parameters
    ----------
    station
        Station name.
    latitude
        Station latitude.
    longitude
        Station longitude.
    distance
        Distance from master event to station in degrees.
    azimuth
        Azimuth from master event to station in degrees.
    phase
        Phase name.
    time
        Predicted travel time in second.
    dtdd
        Horizontal slowness in s/deg.
    dtdh
        Vertical slowness in s/km.
    dt
        Travel time difference in seconds.
    cc
        Cross-correlation coefficient. cc=0.0 means no cross-correlation is applied.
    weight
        Weight for the observation.

    Attributes
    ----------
    dt_pre : float
        Predicted travel time difference for a given solution.
    residual : float
        Travel time difference residual for a given solution.
    """

    station: str
    latitude: float
    longitude: float
    distance: float
    azimuth: float
    phase: str
    time: float
    dtdd: float
    dtdh: float
    dt: float
    cc: float = 0.0
    weight: float = 1.0


class Solution:
    """
    Class for solution.
    """

    def __init__(self, params, type):
        """
        Parameters
        ----------
        params : tuple
            Solution parameters. The values depend on the solution type. For
            ``type='geographic'``, the tuple should be (dlat, dlon, ddepth), where dlat
            and dlon are in degrees and ddepth is in km. For ``type='cylindrical'``, the
            tuple should be (ddist, az, ddepth), where ddist is in meter, az is in
            degrees, and ddepth is in meter.
        type : str
            Solution type, either 'geographic' or 'cylindrical'.

        Attributes
        ----------
        tmean : float
            Mean travel time residual used as the origin time correction.
        misfit : float
            RMS of travel time residuals.
        """
        self.type = type
        match self.type:
            case "geographic":
                self.dlat, self.dlon, self.ddepth = params
            case "cylindrical":
                self.ddist, self.az, self.ddepth = params
            case _:
                raise ValueError(f"Unrecognized solution type '{type}'.")

    def __str__(self):
        match self.type:
            case "geographic":
                result = [
                    f"dlat: {self.dlat}°",
                    f"dlon: {self.dlon}°",
                    f"ddepth: {self.ddepth} km",
                ]
            case "cylindrical":
                result = [
                    f"ddist: {self.ddist} m",
                    f"az: {self.az}°",
                    f"ddepth: {self.ddepth} m",
                ]

        for attr in ["tmean", "misfit"]:
            if hasattr(self, attr):
                result.append(f"{attr}: {getattr(self, attr):.3f}")
        return "\n".join(result)

    def to_event(self, master, slave=None):
        """
        Convert the solution to absolute time and location.

        Parameters
        ----------
        master : Event
            Master event.
        slave : Event
            Slave event.
        """
        origin = (master.origin if slave is None else slave.origin) + self.tmean
        magnitude = master.magnitude if slave is None else slave.magnitude
        match self.type:
            case "geographic":
                latitude = master.latitude + self.dlat
                longitude = master.longitude + self.dlon
                depth = master.depth + self.ddepth
            case "cylindrical":
                earth_radius = 6371.0  # km
                ddist = self.ddist / 1000.0  # convert distance from meter to km
                azimuth = np.radians(self.az)  # convert azimuth from degree to radian
                latitude, longitude = np.radians([master.latitude, master.longitude])
                latitude += ddist / earth_radius * np.cos(azimuth)
                longitude += ddist / earth_radius * np.sin(azimuth) / np.cos(latitude)
                latitude, longitude = np.degrees([latitude, longitude])
                depth = master.depth + self.ddepth / 1000.0

        return Event(
            origin=origin,
            latitude=latitude,
            longitude=longitude,
            depth=depth,
            magnitude=magnitude,
        )
