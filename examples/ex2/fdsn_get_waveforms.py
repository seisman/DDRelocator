"""
Download seismic waveforms from multiple data centers via the FDSN web services.

This script extends ObsPy's MassDownloader module to allow more flexible data
selection and downloading.

Author:
    Dongdong Tian @ CUG (dtian@cug.edu.cn)
Revision History:
    2023/05/12    Initial version.
    2023/08/15    Support reading catalog from a CSV file.
    2023/08/15    Support selecting FDSN data centers.
"""
import sys

import pandas as pd
from obspy import Catalog, UTCDateTime, read_events, read_inventory
from obspy.clients.fdsn.mass_downloader import Domain, MassDownloader, Restrictions
from obspy.core.event import Event, Magnitude, Origin
from obspy.geodetics import gps2dist_azimuth, kilometers2degrees
from obspy.taup import TauPyModel


def read_events_from_csv(filename):
    """
    Read events from a CSV file.

    The CSV file should contain the following columns:

    - time
    - longitude
    - latitude
    - depth (in km)
    - magnitude
    """
    df = pd.read_csv(filename)
    cat = Catalog()
    for _, row in df.iterrows():
        origin = Origin(
            time=UTCDateTime(row["time"]),
            longitude=row["longitude"],
            latitude=row["latitude"],
            depth=row["depth"] * 1000.0,
        )
        magnitude = Magnitude(mag=row["magnitude"])
        event = Event(origins=[origin], magnitudes=[magnitude])
        cat.append(event)
    return cat


class ComplexDomain(Domain):
    """
    A custom domain to select stations based on combinations of multiple criteria.

    - Rectangular domain with min/max latitude/longitude in degrees
    - Circular domain with a center point and min/max radius in degrees

    Parameters
    ----------
    minlatitude : float
        The minimum latitude in degrees.
    maxlatitude : float
        The maximum latitude in degrees.
    minlongitude : float
        The minimum longitude in degrees.
    maxlongitude : float
        The maximum longitude in degrees.
    latitude : float
        The latitude of the center point in degrees.
    longitude : float
        The longitude of the center point in degrees.
    minradius : float
        The minimum radius in degrees.
    maxradius : float
        The maximum radius in degrees.
    """

    def __init__(
        self,
        minlatitude=None,
        maxlatitude=None,
        minlongitude=None,
        maxlongitude=None,
        latitude=None,
        longitude=None,
        minradius=None,
        maxradius=None,
    ):
        # rectangular domain with min/max latitude/longitude in degrees
        self.minlatitude = minlatitude
        self.maxlatitude = maxlatitude
        self.minlongitude = minlongitude
        self.maxlongitude = maxlongitude
        # circular domain with minradius and maxradius in degrees
        self.latitude = latitude
        self.longitude = longitude
        self.minradius = minradius
        self.maxradius = maxradius

        # rectangle and/or circular domain?
        self.rectangle_domain = False
        self.circle_domain = False
        if all(
            v is not None
            for v in [minlatitude, maxlatitude, minlongitude, maxlongitude]
        ):
            self.rectangle_domain = True
        if all(v is not None for v in [latitude, longitude, minradius, maxradius]):
            self.circle_domain = True

    def get_query_parameters(self):
        """
        Return the query parameters for the domain used by get_stations().

        The returned query parameters must be a rectangular domain or a circular
        domain, but not both.

        When both rectangular and circular domains are specified, the rectangle
        domain will be used as the query parameters of the FDSN web services.
        The circular domain will be processed in the `is_in_domain` function.
        """
        if self.rectangle_domain:
            return {
                "minlatitude": self.minlatitude,
                "maxlatitude": self.maxlatitude,
                "minlongitude": self.minlongitude,
                "maxlongitude": self.maxlongitude,
            }
        if self.circle_domain:
            return {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "minradius": self.minradius,
                "maxradius": self.maxradius,
            }
        return {}

    def is_in_domain(self, latitude, longitude):
        """
        Return True if the given latitude and longitude are in the domain.

        This function is used to refine the domain after the data has been downloaded.
        """
        # Possible cases:
        #
        # 1. rectangular domain only: already processed by get_query_parameters()
        # 2. circular domain only: already processed by get_query_parameters()
        # 3. rectangular and circular domain: rectangular domain is used for
        #    get_query_parameters(), circular domain is used for is_in_domain()
        # 4. no domain: i.e., global doamin, return True
        if self.rectangle_domain and self.circle_domain:
            gcdist = kilometers2degrees(
                gps2dist_azimuth(self.latitude, self.longitude, latitude, longitude)[0]
                / 1000.0
            )
            return bool(self.minradius <= gcdist <= self.maxradius)
        return True


def event_get_waveforms(
    event,
    minradius=0.0,
    maxradius=180.0,
    startrefphase=None,
    endrefphase=None,
    startoffset=0.0,
    endoffset=0.0,
    providers=None,
    restriction_kwargs={},
):
    """
    Get waveforms for an event from multiple data centers via the FDSN web services.

    Parameters
    ----------
    event : obspy.core.event.Event
        The event for which to download the waveforms.
    minradius : float
        The minimum radius for stations away from the epicenter in degrees.
    maxradius : float
        The maximum radius for stations away from the epicenter in degrees.
    startrefphase : str or None
        The reference phase to use for the start time. None means the origin time.
    endrefphase : str or None
        The reference phase to use for the end time. None means the origin time.
    startoffset : float
        The time in seconds to add to the start time.
    endoffset : float
        The time in seconds to add to the end time.
    providers : list of str or None
        List of FDSN client names or service URLS. None means all available clients.
    """
    origin = event.preferred_origin() or event.origins[0]  # event origin
    eventid = origin.time.strftime("%Y%m%d%H%M%S")  # event ID based on origin time

    mseed_storage = (
        f"mseed/{eventid}/"
        + "{network}.{station}.{location}.{channel}__{starttime}__{endtime}.mseed"
    )
    stationxml_storage = f"stations/{eventid}/" + "{network}.{station}.xml"

    domains, restrictions = [], []
    if not startrefphase and not endrefphase:
        # Reference phases are not given. Use origin time.
        domains.append(
            ComplexDomain(
                latitude=origin.latitude,
                longitude=origin.longitude,
                minradius=minradius,
                maxradius=maxradius,
            )
        )
        restrictions.append(
            Restrictions(
                starttime=origin.time + startoffset,
                endtime=origin.time + endoffset,
                **restriction_kwargs,
            )
        )
    elif startrefphase and endrefphase:
        # Reference phases are given. Use the reference phases.
        model = TauPyModel(model="iasp91")
        radinc = 5
        for radius in range(0, 181, radinc):  # loop over epicentral distances
            if radius + radinc < minradius or radius > maxradius:
                continue
            phasetime = model.get_travel_times(
                source_depth_in_km=origin.depth / 1000.0,
                distance_in_degree=max(radius, minradius),
                phase_list=startrefphase,
            )[0].time
            starttime = origin.time + phasetime + startoffset
            phasetime = model.get_travel_times(
                source_depth_in_km=origin.depth / 1000.0,
                distance_in_degree=min(radius + radinc, maxradius),
                phase_list=endrefphase,
            )[-1].time
            endtime = origin.time + phasetime + endoffset

            domains.append(
                ComplexDomain(
                    latitude=origin.latitude,
                    longitude=origin.longitude,
                    minradius=max(radius, minradius),
                    maxradius=min(radius + radinc, maxradius),
                )
            )
            restrictions.append(
                Restrictions(starttime=starttime, endtime=endtime, **restriction_kwargs)
            )
    else:
        raise ValueError(
            "startrefphase and endrefphase must be either both or neither."
        )

    mdl = MassDownloader(providers=providers)
    for domain, restriction in zip(domains, restrictions):
        mdl.download(
            domain,
            restriction,
            mseed_storage=mseed_storage,
            stationxml_storage=stationxml_storage,
        )


if len(sys.argv) == 1:
    sys.exit(f"Usage: python {sys.argv[0]} catalog.quakeml/catalog.csv")

if sys.argv[1].endswith(".quakeml"):
    cat = read_events(sys.argv[1])
elif sys.argv[1].endswith(".csv"):
    cat = read_events_from_csv(sys.argv[1])

inv = read_inventory("1995-stations.xml")

restriction_kwargs = dict(
    limit_stations_to_inventory=inv,
    reject_channels_with_gaps=False,
    minimum_length=0.5,
    channel="BHZ",
    sanitize=True,
)

for ev in cat:
    event_get_waveforms(
        ev,
        minradius=0.0,
        maxradius=117,
        startrefphase=["p", "P", "Pdiff"],
        endrefphase=["p", "P", "Pdiff"],
        startoffset=-60,
        endoffset=120,
        restriction_kwargs=restriction_kwargs,
    )
    event_get_waveforms(
        ev,
        minradius=117,
        maxradius=180,
        startrefphase=["PKP", "PKIKP", "PKiKP"],
        endrefphase=["PKP", "PKIKP", "PKiKP"],
        startoffset=-120,
        endoffset=240,
        restriction_kwargs=restriction_kwargs,
    )
