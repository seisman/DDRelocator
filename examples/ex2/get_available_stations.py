from obspy.clients.fdsn import RoutingClient

client = RoutingClient("iris-federator")
inv = client.get_stations(
    starttime="1995-11-14T00:00:00.000",
    endtime="1995-11-14T23:59:59.999",
    channel="BHZ",
    level="station",
)
inv.write("1995-stations.xml", format="stationxml")
