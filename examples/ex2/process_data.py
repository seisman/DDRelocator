"""
ex2: process miniseed data and save as SAC format.
"""

from dataclasses import dataclass
from pathlib import Path

from ddrelocator.helpers import read_events_from_csv
from obspy import read, read_inventory
from obspy.geodetics import gps2dist_azimuth
from obspy.io.sac import SACTrace


@dataclass
class Channel3C:
    network: str
    station: str
    location: str
    channel: str
    coord: dict


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

# Read waveforms and inventories of the two events
st1 = read(f"mseed/{ev1.id}/*.mseed")
inv1 = read_inventory(f"stations/{ev1.id}/*.xml")

st2 = read(f"mseed/{ev2.id}/*.mseed")
inv2 = read_inventory(f"stations/{ev2.id}/*.xml")

# Find the common stations.
# Here, common means "network.station" is the same. The location code may change!
common_stations = set(f"{tr.stats.network}.{tr.stats.station}" for tr in st1) & set(
    f"{tr.stats.network}.{tr.stats.station}" for tr in st2
)

# Only keep the common stations for the two events.
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

    # Rotate horizontal components to RT components.
    # As in ObsPy v1.4, the rotate method 'NE->RT' doesn't take component azimuth into
    # account. So we need to use '->ZNE' first then 'NE->RT'.
    st_RT = st.copy()

    # Create a dictionary of Channel3C objects.
    channel3c = {}
    for tr in st_RT:
        key = tr.id[:-1]
        if key not in channel3c:
            network, station, location, channel = key.split(".")
            coord = inv.get_coordinates(tr.id, datetime=ev.origin)
            channel3c[key] = Channel3C(network, station, location, channel, coord)

        # Add back azimuth information to traces so that 'NE->RT' can work properly.
        tr.stats.back_azimuth = gps2dist_azimuth(
            ev.latitude, ev.longitude, coord["latitude"], coord["longitude"]
        )[2]

    # Remove traces that don't have all 3 components and the horizontal components are
    # not orthogonal.
    for chn3c in channel3c.values():
        rtz = st_RT.select(
            network=chn3c.network,
            station=chn3c.station,
            location=chn3c.location,
            channel=f"{chn3c.channel}?",
        )
        if len(rtz) != 3:  # Need all three components
            for _ in rtz:
                st_RT.remove(_)
            continue

        # Check if the remaining components are N and E
        rtz.remove(rtz.select(component="Z")[0])
        tr1, tr2 = rtz
        cmpaz1 = inv.get_orientation(tr1.id, datetime=ev.origin)["azimuth"]
        cmpaz2 = inv.get_orientation(tr2.id, datetime=ev.origin)["azimuth"]
        if not (89 <= abs(cmpaz1 - cmpaz2) <= 90.0):
            for _ in rtz:
                st_RT.remove(_)
            continue

    # Rotation
    st_RT.rotate(method="->ZNE", inventory=inv, components=["ZNE", "Z12", "123"])
    st_RT.rotate(method="NE->RT")
    for tr in st_RT.select(component="Z"):  # Z component is not needed
        st_RT.remove(tr)

    Path(f"SAC/{ev.id}").mkdir(parents=True, exist_ok=True)
    for tr in st + st_RT:
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
        coord = channel3c[tr.id[:-1]].coord
        sac.stla = coord["latitude"]
        sac.stlo = coord["longitude"]
        sac.stel = coord["elevation"]
        sac.stdp = coord["local_depth"]

        if tr.stats.channel[-1] not in "RT":  # ZNE components
            # set channel orientation
            orient = inv.get_orientation(tr.id, datetime=ev.origin)
            # Need to cautious with the different definitions of 'dip'
            # In ObsPy, 'dip' is degrees, down from horizontal [-90, 90].
            # In SAC, 'dip' is degrees, down from vertical-up [0, 180].
            sac.cmpinc = orient["dip"] + 90.0
            sac.cmpaz = orient["azimuth"]

        # set SAC header
        sac.lcalda = True  # calculate distance, azimuth and back-azimuth in saving
        print(f"SAC/{ev.id}/{tr.id}.SAC")
        sac.write(f"SAC/{ev.id}/{tr.id}.SAC")
