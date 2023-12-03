"""
Classes for ddrelocator.
"""
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
        return f"{self.origin} {self.latitude} {self.longitude} {self.depth}"


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
        use=1,
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
        use : int
            Used in relocation or not. 1 for use, 0 for not use.

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
        self.use = use


class Solution:
    """
    Class for solution.
    """

    def __init__(self, dlat, dlon, ddepth, master):
        """
        Parameters
        ----------
        dlat : float
            Latitude difference in degrees.
        dlon : float
            Longitude difference in degrees.
        ddepth : float
            Depth difference in km.
        master : Event
            Master event.

        Attributes
        ----------
        latitude : float
            Absolute latitude.
        longitude : float
            Absolute longitude.
        depth : float
            Absolute depth.
        tmean : float
            Mean travel time residual used as the origin time correction.
        misfit : float
            RMS of travel time residuals.
        """
        # location difference
        self.dlat = dlat
        self.dlon = dlon
        self.ddepth = ddepth
        # absolute location
        self.latitude = master.latitude + dlat
        self.longitude = master.longitude + dlon
        self.depth = master.depth + ddepth

    def __str__(self):
        result = f"dlat: {self.dlat}, dlon: {self.dlon}, ddepth: {self.ddepth}"
        if hasattr(self, "tmean"):
            result += f", tmean: {self.tmean:.3f}"
        if hasattr(self, "misfit"):
            result += f", misfit: {self.misfit:.3f}"
        return result


class SearchParams:
    """
    Class for search parameters.
    """

    def __init__(self, dlats, dlons, ddeps):
        """
        Parameters
        ----------
        dlats : slice
            slice(dlat_min, dlat_max, dlat_step)
        dlons : slice
            slice(dlon_min, dlon_max, dlon_step)
        ddeps : slice
            slice(ddep_min, ddep_max, ddep_step)
        """
        self.dlats = dlats
        self.dlons = dlons
        self.ddeps = ddeps
