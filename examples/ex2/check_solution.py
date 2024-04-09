"""
ex2: Check a solution.
"""

import matplotlib.pyplot as plt
from ddrelocator import Event, Solution, try_solution
from ddrelocator.helpers import read_obslist
from obspy import read

# Event information
ev1 = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
ev2 = Event("1995-11-14T06:32:55.750", -3.682, 101.924, 57.0, 5.1)

# read obslist
obslist = read_obslist("obs-2003-1995.dat")

# Check two solutions:
#
# 1. Yang et al., 2021, SRL
# ddist, az, ddepth, tmean = 251.0, 272.0, -500, 1.9186
# ddist, az, ddepth, tmean = 251.0, 272.0, 500, 1.9186
# ddist, az, ddepth, tmean = 251.0, 272.0, -499, 1.9695
# ddist, az, ddepth, tmean = 251.0, 272.0, 499, 1.9695

# 2. Zhang & Wen, 2023, SRL
ddist, az, ddepth, tmean = 407.0, 137.0, 58, 1.9227

sol = Solution((ddist, az, ddepth), type="cylindrical")
try_solution(ev1, obslist, sol, keep_residual=True)
for obs in obslist:
    obs.residual += sol.tmean
sol.tmean = tmean  # force the tmean to the reported value
for obs in obslist:
    obs.residual -= sol.tmean

# read traces for plotting
st1 = read(f"SAC/{ev1.id}/*Z.SAC")
st2 = read(f"SAC/{ev2.id}/*Z.SAC")

st1.filter("bandpass", freqmin=0.5, freqmax=3.0, corners=4, zerophase=False)
st2.filter("bandpass", freqmin=0.5, freqmax=3.0, corners=4, zerophase=False)

t0, t1 = -4.0, 8.0
fig, ax = plt.subplots(1, 1, figsize=(6, 30))
ax.get_yaxis().set_visible(False)

count = 1
for obs in obslist:
    network, station = obs.station.split(".")
    tr1 = st1.select(network=network, station=station)[0]
    tr2 = st2.select(network=network, station=station)[0]

    shift = obs.dt_pre + sol.tmean
    tr1.trim(ev1.origin + obs.time + t0, ev1.origin + obs.time + t1)
    tr2.trim(ev2.origin + obs.time + t0 + shift, ev2.origin + obs.time + t1 + shift)
    tr1.normalize()
    tr2.normalize()

    ax.plot(tr1.times() + t0, tr1.data * 0.5 + count, "k", lw=0.75)
    ax.plot(tr2.times() + t0, tr2.data * 0.5 + count, "b", lw=0.75)
    ax.text(
        t0 - 0.5,
        count,
        f"{obs.station} ({obs.phase})",
        ha="right",
        va="center",
        fontsize=8,
    )
    ax.text(
        t0,
        count + 0.2,
        f"{obs.residual:.3f}",
        ha="left",
        va="center",
        fontsize=8,
    )
    ax.set_title(
        f"Event: {ev1.id} (black) / {ev2.id} (blue)\n"
        f"Solution: {sol.ddist:.1f} m, {sol.az:.1f} deg, {sol.ddepth:.0f} m, {sol.tmean:.4f} s"
    )

    count += 1

plt.show()
fig.savefig("waveform-alignment.pdf")
