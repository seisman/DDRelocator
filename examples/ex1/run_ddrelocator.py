"""
ex1: Run ddrelocator.
"""

import time

from ddrelocator import Event, find_solution, try_solution
from ddrelocator.helpers import dump_solutions, read_obslist
from ddrelocator.plotting import plot_dt, plot_misfit, plot_residual

# Information of the master event [known]
master = Event("2018-02-01T00:00:00", 36.1688, 139.8075, 53.45, 4.7)
# Information of the slave event [unknown]
slave = Event("2018-02-02T00:00:00", 36.1678, 139.8095, 53.45, 4.7)

# Observation file
obsfile = "obs.dat"

# Search parameters
"""
sol_type = "geographic"  # dlat, dlon and ddepth
ranges = (
    slice(-0.002, 0.002, 0.0002),  # dlat in degree
    slice(-0.004, 0.004, 0.0002),  # dlon in degree
    slice(-1, 1, 0.01),  # ddepth in km
)
"""
sol_type = "cylindrical"  # ddist, azimuth, and ddepth
ranges = (
    slice(0, 300, 5),  # ddist in meter
    slice(0, 360, 5),  # az in degree
    slice(-1000, 1000, 10),  # ddepth in meter
)

print("Ex1 for ddrelocator")
print("Master event: ", master)
print("Slave event: ", slave)

# Read observations from a file
obslist = read_obslist(obsfile)
print(f"Read {len(obslist)} observations from {obsfile}")

# Visualize the observations
plot_dt(obslist, master)

# Relocate the slave event relative to the master event
print("Grid search...  ", end="")
start = time.time()
sol, grid, Jout = find_solution(master, obslist, ranges, sol_type)
print(f"Done in {time.time() - start:.1f} sec")

# Try the best solution again to add more properties like tmean and residuals
try_solution(master, obslist, sol, keep_residual=True)
# The best location for the slave event
slave_sol = sol.to_event(master, slave)
print("Best solution:")
print(sol)
print("Slave event: ", slave_sol)

# Visualize the residuals
plot_residual(obslist, master, slave_sol)

# Visualize the misfit
plot_misfit(grid, Jout, sol_type)

# Save the solutions into a pickle file so it can be reused
dump_solutions(grid, Jout, "solutions.pkl")
