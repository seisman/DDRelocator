"""
Download seismic waveforms from multiple data centers via the FDSN web services.
"""
import sys

import pandas as pd
from obspy import Catalog, UTCDateTime, read_events, read_inventory
from obspy.clients.fdsn.mass_downloader import (
    CircularDomain,
    MassDownloader,
    Restrictions,
)
from obspy.core.event import Event, Magnitude, Origin


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


def event_get_waveforms(
    event,
    minradius,
    maxradius,
    starttime,
    endtime,
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
    starttime : str
        The start time in ISO format.
    endtime : str
        The end time in ISO format.
    restriction_kwargs : dict
        Keyword arguments for obspy.clients.fdsn.mass_downloader.Restrictions.
    """
    origin = event.preferred_origin() or event.origins[0]  # event origin
    eventid = origin.time.strftime("%Y%m%d%H%M%S")  # event ID based on origin time

    mseed_storage = (
        f"mseed/{eventid}/"
        + "{network}.{station}.{location}.{channel}__{starttime}__{endtime}.mseed"
    )
    stationxml_storage = f"stations/{eventid}/" + "{network}.{station}.xml"

    domain = CircularDomain(
        longitude=origin.longitude,
        latitude=origin.latitude,
        minradius=minradius,
        maxradius=maxradius,
    )
    restriction = Restrictions(
        starttime=starttime,
        endtime=endtime,
        **restriction_kwargs,
    )

    # For unknown reasons, providers=None does not work.
    mdl = MassDownloader(providers=["IRIS", "SCEDC", "AUSPASS"])
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
    origin = ev.preferred_origin() or ev.origins[0]
    event_get_waveforms(
        ev,
        minradius=0.0,
        maxradius=30,
        starttime=origin.time - 60,
        endtime=origin.time + 600,
        restriction_kwargs=restriction_kwargs,
    )
    event_get_waveforms(
        ev,
        minradius=30,
        maxradius=90,
        starttime=origin.time + 300,
        endtime=origin.time + 900,
        restriction_kwargs=restriction_kwargs,
    )
    event_get_waveforms(
        ev,
        minradius=90,
        maxradius=180,
        starttime=origin.time + 600,
        endtime=origin.time + 1400,
        restriction_kwargs=restriction_kwargs,
    )
