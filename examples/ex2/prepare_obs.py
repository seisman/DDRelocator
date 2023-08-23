"""
ex2: Prepare observations.
"""
import matplotlib.pyplot as plt
import numpy as np
from ddrelocator import Obs
from ddrelocator.helpers import distaz, dump_obslist, get_ttime_slowness
from obspy import UTCDateTime, read
from obspy.signal.cross_correlation import correlate, correlate_template, xcorr_max
from obspy.taup import TauPyModel


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


# Event informatio
ev1 = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
ev2 = Event("1995-11-14T06:32:55.750", -3.682, 101.924, 57.0, 5.1)

st1 = read(f"SAC/{ev1.id}/*.SAC")
st2 = read(f"SAC/{ev2.id}/*.SAC")

model = TauPyModel(model="iasp91")
# start and end time for the signal window, relative to predicted time
t0, t1 = -2.0, 8.0

obslist = []
fig, ax = plt.subplots(1, 1, figsize=(6, 30))
ax.get_yaxis().set_visible(False)

count = 1
print("station latitude longitude distance azimuth phase dtdd dtdh dt use")
for tr1 in st1:  # loop over traces of the master event
    st_match = st2.select(
        network=tr1.stats.network, station=tr1.stats.station, channel=tr1.stats.channel
    )
    if len(st_match) == 0:
        print(f"{tr1.id}: no matched trace.")
    elif len(st_match) == 1:
        tr2 = st_match[0]
    else:
        print(f"{tr1.id}: {len(st_match)} traces found. Use the first one.")
        tr2 = st_match[0]

    # calculate distance and azimuth from the master event to the station
    dist, az = distaz(
        ev1.latitude, ev1.longitude, tr1.stats.sac.stla, tr1.stats.sac.stlo
    )

    phase = ["p", "P", "Pdiff"] if dist < 117 else ["PKP", "PKIKP", "PKiKP"]

    # get travel time, horizontal slowness and vertical slowness
    name, ttime, dtdd, dtdh = get_ttime_slowness(model, ev1.depth, dist, phase)

    # cut the signal of the master event around the predicted phase time.
    tr1.trim(ev1.origin + ttime + t0, ev1.origin + ttime + t1)
    if len(tr1) == 0 or len(tr2) == 0:
        print(f"{tr1.id}: skipped due to zero-length.")
        continue

    # resample to 1000 Hz to have superhigh resolution in CC
    tr1.resample(sampling_rate=1000)
    tr2.resample(sampling_rate=1000)

    # Do CC between tr1 and tr2.
    cc = correlate_template(tr2, tr1, mode="valid", normalize="full")
    idx = np.argmax(np.abs(cc))  # index of the max CC value
    value = cc[idx]  # max CC value. Maybe negative
    # time shift of tr2 to match tr1
    shift = tr2.stats.starttime - (ev2.origin + ttime + t0) + idx * tr2.stats.delta
    tr2.trim(ev2.origin + ttime + t0 + shift, ev2.origin + ttime + t1 + shift)
    tr1.normalize()
    tr2.normalize()

    if value < 0.8:
        continue
    count += 1

    station = f"{tr1.stats.network}.{tr1.stats.station}"
    obslist.append(
        Obs(
            station,
            tr1.stats.sac.stla,
            tr1.stats.sac.stlo,
            dist,
            az,
            name,
            ttime,
            dtdd,
            dtdh,
            shift,
            1,  # use this observation
        )
    )

    ax.plot(tr1.times() + t0, tr1.data * 0.5 + count, "b", lw=1.0)
    ax.plot(tr2.times() + t0, tr2.data * 0.5 + count, "r", lw=1.0)
    ax.text(t0 - 0.5, count, f"{station} ({name})", ha="right", va="center", fontsize=8)
    ax.text(
        t0,
        count + 0.2,
        f"{shift:.3f} ({value:.2f})",
        ha="left",
        va="center",
        fontsize=8,
    )

plt.tight_layout()
plt.show()

dump_obslist(obslist, "obs-2003-1995.dat")
