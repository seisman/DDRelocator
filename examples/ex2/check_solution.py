# %%
import matplotlib.pyplot as plt
import numpy as np
from ddrelocator import Solution, try_solution
from ddrelocator.helpers import read_obslist
from obspy import UTCDateTime, read
from obspy.geodetics import kilometers2degrees


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

# read obslist
obslist = read_obslist("obs-2003-1995.dat")

# Yang et al., 2021, SRL
"""
ddist, daz, tmean = 251.0, 272.0, 1.9186  # ddist in meter
sol = Solution(
    dlat=kilometers2degrees(ddist * np.cos(np.deg2rad(daz)) / 1000.0),
    dlon=kilometers2degrees(ddist * np.sin(np.deg2rad(daz)) / 1000.0),
    ddepth=-0.5,
    master=ev1,
)
"""
# Zhang & Wen, 2023, SRL
ddist, daz, tmean = 407.0, 137.0, 1.9227  # ddist in meter
sol = Solution(
    dlat=kilometers2degrees(ddist * np.cos(np.deg2rad(daz)) / 1000.0),
    dlon=kilometers2degrees(ddist * np.sin(np.deg2rad(daz)) / 1000.0),
    ddepth=0.058,
    master=ev1,
)

try_solution(obslist, sol)
for obs in obslist:
    obs.residual += sol.tmean
sol.tmean = tmean  # force the tmean to the reported value
for obs in obslist:
    obs.residual -= sol.tmean

# read traces for plotting
st1 = read(f"SAC/{ev1.id}/*.SAC")
st2 = read(f"SAC/{ev2.id}/*.SAC")

t0, t1 = -2.0, 8.0
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

    ax.plot(tr1.times() + t0, tr1.data * 0.5 + count, "k", lw=1)
    ax.plot(tr2.times() + t0, tr2.data * 0.5 + count, "b", lw=1)
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

    count += 1

plt.show()
fig.savefig("waveform-alignment.pdf")
