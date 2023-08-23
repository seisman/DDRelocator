"""
ex1: Prepare synthetic observations.
"""
from ddrelocator.ddrelocator import Event, Obs, Station
from ddrelocator.helpers import dump_obslist, get_ttime_slowness
from obspy.geodetics import gps2dist_azimuth, kilometers2degrees
from obspy.taup import TauPyModel

# 1. Define a master event and a slave event.
#
# The master event is the reference event, and the slave event is the event
# to be relocated, relative to the master event.
master = Event("2018-02-01T00:00:00", 36.1688, 139.8075, 53.45, 4.7)
slave = Event("2018-02-02T00:00:00", 36.1678, 139.8095, 53.45, 4.7)

# 2. Define a series of stations
stations = [
    Station("ISSH", 36.3143, 139.185, 0.0),
    Station("MNAH", 36.0715, 139.099, 0.0),
    Station("HHNH", 35.8637, 139.273, 0.0),
    Station("IWTH", 35.929, 139.735, 0.0),
    Station("SHMH", 35.7966, 140.021, 0.0),
    Station("NRTH", 35.8307, 140.298, 0.0),
    Station("KGRH", 36.0864, 140.314, 0.0),
    Station("TSKH", 36.2137, 140.089, 0.0),
    Station("IWSH", 36.3701, 140.14, 0.0),
    Station("MOKH", 36.4458, 139.951, 0.0),
    Station("IICH", 36.7084, 139.769, 0.0),
    Station("AWNH", 36.5509, 139.615, 0.0),
    Station("MDRH", 36.4931, 139.322, 0.0),
]

# 3. Prepare observations.
#
# Use the IASP91 model to calculate the theoretical traveltime.
phase = "p"
model = TauPyModel(model="iasp91")
# Create a list of Obs objects.
obslist = []
for sta in stations:
    # calculate distance and azimuth from the master event to the station
    dist, az = gps2dist_azimuth(
        master.latitude, master.longitude, sta.latitude, sta.longitude
    )[0:2]
    dist = kilometers2degrees(dist / 1000.0)  # convert distance from m to degree
    # get phase name, travel time, horizontal slowness and vertical slowness
    phasename, t0, dtdd, dtdh = get_ttime_slowness(model, master.depth, dist, [phase])

    # calculate the traveltime of the slave event
    dist1 = gps2dist_azimuth(
        slave.latitude, slave.longitude, sta.latitude, sta.longitude
    )[0]
    dist1 = kilometers2degrees(dist1 / 1000.0)
    t1 = get_ttime_slowness(model, slave.depth, dist1, [phase])[1]

    # Theoretical traveltime difference between the master and slave events.
    dt = t1 - t0

    obslist.append(
        Obs(
            sta.name,
            sta.latitude,
            sta.longitude,
            dist,
            az,
            phasename,
            t0,
            dtdd,
            dtdh,
            dt,
            1,  # use this observation
        )
    )

# 4. Dump the observations into a file.
# We can use the read_obslist() function to read the observations back from a file to a list.
# It's useful when we want to modify the observations manually.
dump_obslist(obslist, "obs.dat")
