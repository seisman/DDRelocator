"""
ex2: process miniseed data and save as SAC format.
"""

from pathlib import Path

from helpers import read_events_from_csv
from obspy import read, read_inventory
from obspy.io.sac import SACTrace

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

# Read the event pair
ev1, ev2 = read_events_from_csv("catalog.csv")
print("Event 1: ", ev1)
print("Event 2: ", ev2)

# read waveforms and inventories of the two events
st1 = read(f"mseed/{ev1.id}/*.mseed")
inv1 = read_inventory(f"stations/{ev1.id}/*.xml")

st2 = read(f"mseed/{ev2.id}/*.mseed")
inv2 = read_inventory(f"stations/{ev2.id}/*.xml")

# find the common stations
# here, common means "network.station" is the same. The location code may change!
common_stations = set(f"{tr.stats.network}.{tr.stats.station}" for tr in st1) & set(
    f"{tr.stats.network}.{tr.stats.station}" for tr in st2
)

# only keep the common stations for the two events
for st in (st1, st2):
    for tr in st:
        if f"{tr.stats.network}.{tr.stats.station}" not in common_stations:
            st.remove(tr)

for st, inv, ev in [(st1, inv1, ev1), (st2, inv2, ev2)]:
    # Merge and remove instrumental responses to WWSP
    st.merge(fill_value="interpolate")
    st.remove_response(
        inventory=inv,
        output="DISP",
        pre_filt=(0.01, 0.02, 8, 10),
        zero_mean=True,
        taper=True,
        taper_fraction=0.05,
    )
    st.simulate(paz_simulate=paz_wwsp)

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
        coord = inv.get_coordinates(tr.id, datetime=ev.origin)
        sac.stla = coord["latitude"]
        sac.stlo = coord["longitude"]
        sac.stel = coord["elevation"]
        sac.stdp = coord["local_depth"]

        # set channel orientation
        orient = inv.get_orientation(tr.id, datetime=ev.origin)
        # Need to cautious with the different definitions of 'dip'
        # In ObsPy, 'dip' is degrees, down from horizontal [-90, 90]
        # In SAC, 'dip' is degrees, down from vertical-up [0, 180]
        sac.cmpinc = orient["dip"] + 90.0
        sac.cmpaz = orient["azimuth"]

        # set SAC header
        sac.lcalda = True  # calculate distance, azimuth and back-azimuth in saving
        print(f"SAC/{ev.id}/{tr.id}.SAC")
        sac.write(f"SAC/{ev.id}/{tr.id}.SAC")
