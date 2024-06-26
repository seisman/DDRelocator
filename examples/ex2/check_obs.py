"""
Check the observations by plotting the traces.
"""

import sys

import matplotlib.pyplot as plt
from ddrelocator.helpers import read_events_from_csv, read_obslist
from obspy import read

# t0, t1 = -4.0, 8.0
t0, t1 = 0, 15.0
freqmin, freqmax, corners = 0.5, 3.0, 4

if len(sys.argv) != 2:
    print("Usage: python check_obs.py obsfile")
    sys.exit(1)

obsfile = sys.argv[1]
obslist = read_obslist(obsfile)

ev1, ev2 = read_events_from_csv("catalog.csv")
print("Event 1: ", ev1)
print("Event 2: ", ev2)

# read traces for plotting
st1 = read(f"SAC/{ev1.id}/*Z.SAC")
st2 = read(f"SAC/{ev2.id}/*Z.SAC")

fig, ax = plt.subplots(1, 1, figsize=(7, 22))
ax.get_yaxis().set_visible(False)
for i, obs in enumerate(obslist):
    # Find the corresponding traces
    network, station = obs.station.split(".")
    tr1 = st1.select(network=network, station=station)[0]
    tr2 = st2.select(network=network, station=station)[0]
    # Filter the traces
    tr1.filter(
        "bandpass", freqmin=freqmin, freqmax=freqmax, corners=corners, zerophase=False
    )
    tr2.filter(
        "bandpass", freqmin=freqmin, freqmax=freqmax, corners=corners, zerophase=False
    )

    # Trim and normalize the traces
    tr1.trim(ev1.origin + obs.time + t0, ev1.origin + obs.time + t1)
    tr2.trim(ev2.origin + obs.time + t0 + obs.dt, ev2.origin + obs.time + t1 + obs.dt)
    tr1.normalize()
    tr2.normalize()

    ax.plot(tr1.times() + t0, tr1.data * 0.5 + i, "b", lw=1)
    ax.plot(tr2.times() + t0, tr2.data * 0.5 + i, "r", lw=1)

    ax.text(
        t0 - 1.0, i, f"{obs.station} ({obs.phase})\n {obs.distance:.1f}°", ha="right"
    )
    ax.text(t1 + 0.6, i, f"{obs.dt:.3f} ({obs.cc:.2f})", ha="left")
plt.tight_layout()
plt.show()
