"""
Classes for ddrelocator.
"""

import numpy as np
from obspy import UTCDateTime


class Event:
    """
    Class for event information.
    """

    def __init__(self, origin, latitude, longitude, depth, magnitude=None):
        """
        Parameters
        ----------
        origin : str
            Event origin time.
        latitude : float
            Event latitude.
        longitude : float
            Event longitude.
        depth : float
            Event depth in km.
        magnitude : float
            Event magnitude (unused).

        Attributes
        ----------
        id : str
            Event ID in the format of YYYYMMDDHHMMSS.
        """
        self.origin = UTCDateTime(origin)
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth  # in km
        self.magnitude = magnitude  # unused
        self.id = self.origin.strftime("%Y%m%d%H%M%S")

    def __str__(self):
        return (
            f"{self.origin} {self.latitude:.5f} {self.longitude:.5f} {self.depth:.4f}"
        )


class Station:
    """
    Class for station information.
    """

    def __init__(self, name, latitude, longitude, elevation=0.0):
        """
        Parameters
        ----------
        name : str
            Station name.
        latitude : float
            Station latitude.
        longitude : float
            Station longitude.
        elevation : float
            Station elevation (unused).
        """
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation  # unused


class Obs:
    """
    Class for observations.
    """

    def __init__(
        self,
        station,
        latitude,
        longitude,
        distance,
        azimuth,
        phase,
        time,
        dtdd,
        dtdh,
        dt,
        weight=1.0,
    ):
        """
        Parameters
        ----------
        station : str
            Station name.
        latitude : float
            Station latitude.
        longitude : float
            Station longitude.
        distance : float
            Distance from master event to station in degrees.
        azimuth : float
            Azimuth from master event to station in degrees.
        phase : str
            Phase name.
        time : float
            Predicted travel time in second.
        dtdd : float
            Horizontal slowness in s/deg.
        dtdh : float
            Vertical slowness in s/km.
        dt : float
            Travel time difference.
        weight : float
            Weight for the observation.

        Attributes
        ----------
        dt_pre : float
            Predicted travel time difference for a given solution.
        residual : float
            Travel time difference residual for a given solution.
        """
        self.station = station
        self.latitude = latitude
        self.longitude = longitude
        self.distance = distance
        self.azimuth = azimuth
        self.phase = phase
        self.time = time
        self.dtdd = dtdd
        self.dtdh = dtdh
        self.dt = dt
        self.weight = weight


class Solution:
    """
    Class for solution.
    """

    def __init__(self, params, type):
        """
        Parameters
        ----------
        params : tuple
            Solution parameters. The values depend on the solution type.
            For ``type='geographic'``, the tuple should be (dlat, dlon, ddepth),
            where dlat and dlon are in degrees and ddepth is in km.
            For ``type='cylindrical'``, the tuple should be (ddist, az, ddepth),
            where ddist is in meter, az is in degrees, and ddepth is in meter.
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
        if self.type == "geographic":
            self.dlat, self.dlon, self.ddepth = params
        elif self.type == "cylindrical":
            self.ddist, self.az, self.ddepth = params
        else:
            raise ValueError("Unrecognized solution type '{type}'.")

    def __str__(self):
        if self.type == "geographic":
            result = [
                f"dlat: {self.dlat}°",
                f"dlon: {self.dlon}°",
                f"ddepth: {self.ddepth} km",
            ]
        elif self.type == "cylindrical":
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
        if self.type == "geographic":
            latitude = master.latitude + self.dlat
            longitude = master.longitude + self.dlon
            depth = master.depth + self.ddepth
        elif self.type == "cylindrical":
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
