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
            Use in relocation or not. 0 for not used, 1 for used.

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


class SearchParams:
    """
    Class for search parameters.
    """

    def __init__(self, dlats, dlons, ddeps):
        """
        Parameters
        ----------
        dlats : list or np.ndarray
            List of latitude differences to search.
        dlons : list or np.ndarray
            List of longitude differences to search.
        ddeps : list or np.ndarray
            List of depth differences to search.
        """
        self.dlats = dlats
        self.dlons = dlons
        self.ddeps = ddeps
