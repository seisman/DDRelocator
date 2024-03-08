"""
ex2: Prepare observations.
"""

import matplotlib.pyplot as plt
import numpy as np
from ddrelocator import Event, Obs
from ddrelocator.helpers import distaz, dump_obslist, get_ttime_slowness
from obspy import read
from obspy.signal.cross_correlation import correlate_template
from obspy.taup import TauPyModel

# Event information from catalog. The later one (ev1) is the master event.
ev1 = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
ev2 = Event("1995-11-14T06:32:55.750", -3.682, 101.924, 57.0, 5.1)

# read waveforms
st1 = read(f"SAC/{ev1.id}/*.SAC")
st2 = read(f"SAC/{ev2.id}/*.SAC")

model = TauPyModel(model="iasp91")
# start and end time for the signal window, relative to predicted time
t0, t1 = -2.0, 8.0
cc_threshold = 0.8  # CC threshold to accept the observation


def refphase(dist):
    """
    Use different reference phase for different distance.
    """
    return ["p", "P", "Pdiff"] if dist < 117.0 else ["PKP", "PKIKP", "PKiKP"]


fig, ax = plt.subplots(1, 1, figsize=(6, 30))
ax.get_yaxis().set_visible(False)
obslist = []
for tr1 in st1:  # loop over traces of the master event
    # find the slave event trace with the same seed id
    st_match = st2.select(
        network=tr1.stats.network, station=tr1.stats.station, channel=tr1.stats.channel
    )
    if len(st_match) == 0:  # no matched trace. skip.
        print(f"{tr1.id}: no matched trace.")
        continue
    elif len(st_match) == 1:  # one matched trace. use it.
        tr2 = st_match[0]
    else:  # multiple matched traces. use the first one.
        print(f"{tr1.id}: {len(st_match)} traces found. Use the first one.")
        tr2 = st_match[0]

    # calculate distance and azimuth from the master event to the station
    dist, az = distaz(
        ev1.latitude, ev1.longitude, tr1.stats.sac.stla, tr1.stats.sac.stlo
    )

    # get the reference phase name based on distance
    phase = refphase(dist)

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

    if value < cc_threshold:  # skip if CC value is too small
        continue

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
            weight=1.0,  # equal weight
        )
    )

    idx = len(obslist)  # index for plotting
    ax.plot(tr1.times() + t0, tr1.data * 0.5 + idx, "b", lw=1.0)
    ax.plot(tr2.times() + t0, tr2.data * 0.5 + idx, "r", lw=1.0)
    ax.text(t0 - 0.5, idx, f"{station} ({name})", ha="right", va="center", fontsize=8)
    ax.text(
        t0,
        idx + 0.2,
        f"{shift:.3f} ({value:.2f})",
        ha="left",
        va="center",
        fontsize=8,
    )

plt.tight_layout()
plt.show()

# dump the observations to a file
dump_obslist(obslist, "obs-2003-1995.dat")
