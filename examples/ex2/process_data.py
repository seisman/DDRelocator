from pathlib import Path

from obspy import UTCDateTime, read, read_inventory
from obspy.io.sac import SACTrace


class Event:
    """
    Class for event information.
    """

    def __init__(self, origin, latitude, longitude, depth, magnitude):
        self.origin = UTCDateTime(origin)
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth
        self.magnitude = magnitude
        self.id = self.origin.strftime("%Y%m%d%H%M%S")


# The poles and zeros information are from SAC source code `sac/src/icm/wwsp.c`.
paz_wwsp = {
    "poles": [
        -5.0136607 + 6.4615109j,
        -5.0136607 - 6.4615109j,
        -8.2981509 + 0.0j,
        -8.6940765 - 7.1968661j,
        -8.6940765 + 7.1968661j,
    ],
    "zeros": [0j, 0j, 0j],
    "gain": 397.54767,
    "sensitivity": 1.0,
}

# read waveforms and inventories of the two events
ev1 = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
st1 = read(f"mseed/{ev1.id}/*.mseed")
inv1 = read_inventory(f"stations/{ev1.id}/*.xml")

ev2 = Event("1995-11-14T06:32:55.750", -3.682, 101.924, 57.0, 5.1)
st2 = read(f"mseed/{ev2.id}/*.mseed")
inv2 = read_inventory(f"stations/{ev2.id}/*.xml")

# find the common stations
# here, common means "network.station" is the same. The location code may change!
common_stations = set(f"{tr.stats.network}.{tr.stats.station}" for tr in st1) & set(
    f"{tr.stats.network}.{tr.stats.station}" for tr in st2
)

# only keep the common stations for the two event
for st in (st1, st2):
    for tr in st:
        if f"{tr.stats.network}.{tr.stats.station}" not in common_stations:
            st.remove(tr)

for st, inv, ev in [(st1, inv1, ev1), (st2, inv2, ev2)]:
    st.merge(fill_value="interpolate")
    st.detrend("demean")
    st.detrend("linear")
    st.taper(max_percentage=0.05, type="hann")
    st.remove_response(inventory=inv, output="DISP", pre_filt=(0.01, 0.02, 8, 10))
    st.simulate(paz_simulate=paz_wwsp)
    st.filter("bandpass", freqmin=0.6, freqmax=3.0, corners=2, zerophase=False)

    Path(f"SAC/{ev.id}").mkdir(parents=True, exist_ok=True)
    for tr in st:
        sac = SACTrace.from_obspy_trace(tr)

        # set event information
        sac.evla = ev.latitude
        sac.evlo = ev.longitude
        sac.evdp = ev.depth
        sac.mag = ev.magnitude
        sac.reftime = ev.origin
        sac.o = 0.0
        sac.iztype = "io"

        # set station information
        # Sometimes, the returned inventory has an incorrect starttime/endtime,
        # which causes issues below.
        # coord = inv.get_coordinates(tr.id, datetime=ev.origin)
        coord = inv.get_coordinates(tr.id)
        sac.stla = coord["latitude"]
        sac.stlo = coord["longitude"]
        sac.stel = coord["elevation"]
        sac.stdp = coord["local_depth"]

        # set SAC header
        sac.lcalda = True  # calculate distance, azimuth and back-azimuth in saving
        sac.write(f"SAC/{ev.id}/{tr.id}.SAC")
