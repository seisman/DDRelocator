"""
ex2: Prepare observations.
"""

import numpy as np
from ddrelocator import Event, Obs
from ddrelocator.helpers import distaz, dump_obslist, get_ttime_slowness
from obspy import read
from obspy.signal.cross_correlation import correlate_template
from obspy.taup import TauPyModel

# Event information from catalog. The later one (ev1) is the master event.
ev1 = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
ev2 = Event("1995-11-14T06:32:55.750", -3.682, 101.924, 57.0, 5.1)


# Global variables
model = TauPyModel(model="iasp91")
tshift_max = 20.0  # Search in the limited time window around the predicted arrival time


def search_phase_pairs(phase, twin, cc_min, filter_kwargs):
    """
    Search for phase pairs by cross correlations.
    """
    obslist = []  # list to store the observations

    # Read and filter waveforms
    st1 = read(f"SAC/{ev1.id}/*Z.SAC").filter(**filter_kwargs)
    st2 = read(f"SAC/{ev2.id}/*Z.SAC").filter(**filter_kwargs)

    for tr1 in st1:  # Loop over traces of the master event
        # Find the slave event trace with the same seed id
        st_match = st2.select(id=tr1.id)
        match len(st_match):
            case 0:  # no matched trace. skip.
                print(f"{tr1.id}: no matched trace. Skipped.")
                continue
            case 1:  # one matched trace. use it.
                tr2 = st_match[0]
            case _:  # multiple matched traces. use the first one.
                print(f"{tr1.id}: {len(st_match)} traces found. Use the first one.")
                tr2 = st_match[0]

        # Calculate distance and azimuth from the master event to the station
        dist, az = distaz(
            ev1.latitude, ev1.longitude, tr1.stats.sac.stla, tr1.stats.sac.stlo
        )

        # Get travel time, horizontal slowness and vertical slowness
        phasename, ttime, dtdd, dtdh = get_ttime_slowness(
            model, ev1.depth, dist, [phase]
        )
        if phasename is None:  # No arrival found. Skip this station.
            print(f"{tr1.id}: no arrival found. Skipped.")
            continue

        print(tr1.id)
        # Change the reference time from phase arrival time to event origin time
        t0, t1 = ttime + twin[0], ttime + twin[1]
        # Cut the trace of the master event around the predicted phase time.
        tr1.trim(ev1.origin + t0, ev1.origin + t1)
        # Cut the trace of the slave event around the predicted phase time plus the
        # maximum time shift, because we know the time differences won't be too large.
        # This step is important to reduce the computation time.
        tr2.trim(ev2.origin + t0 - tshift_max, ev2.origin + t1 + tshift_max)
        if len(tr1) == 0 or len(tr2) == 0:
            print(f"{tr1.id}: skipped due to zero-length {len(tr1)} {len(tr2)}.")
            continue

        # resample to 1000 Hz to have superhigh resolution in CC
        tr1.resample(sampling_rate=1000)
        tr2.resample(sampling_rate=1000)

        # Do CC between tr1 and tr2.
        cc = correlate_template(tr2, tr1, mode="valid", normalize="full")
        idx = np.argmax(np.abs(cc))  # index of the max CC value
        value = cc[idx]  # max CC value. Maybe negative
        # time shift of tr2 to match tr1
        shift = tr2.stats.starttime - (ev2.origin + t0) + idx * tr2.stats.delta

        # Skip if CC value is too small
        if value < cc_min:
            continue

        obslist.append(
            Obs(
                f"{tr1.stats.network}.{tr1.stats.station}",
                tr1.stats.sac.stla,
                tr1.stats.sac.stlo,
                dist,
                az,
                phasename,
                ttime,
                dtdd,
                dtdh,
                shift,
                cc=value,
                weight=1.0,
            )
        )
    return obslist


filter_kwargs = dict(
    type="bandpass", freqmin=0.5, freqmax=3.0, corners=4, zerophase=False
)
obslist = search_phase_pairs("P", (0, 5.0), 0.9, filter_kwargs)
# obslist = search_phase_pairs("pP", (0, 5.0), 0.9, filter_kwargs)
# obslist = search_phase_pairs("sP", (0, 5.0), 0.9, filter_kwargs)
# obslist = search_phase_pairs("PcP", (0, 5.0), 0.9, filter_kwargs)

# dump the observations to a file
dump_obslist(obslist, "obs-2003-1995.dat")
