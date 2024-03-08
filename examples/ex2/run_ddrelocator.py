"""
ex2: Run ddrelocator.
"""

import time

from ddrelocator import Event, find_solution, try_solution
from ddrelocator.helpers import dump_solutions, read_obslist
from ddrelocator.plotting import plot_dt, plot_misfit, plot_residual

# Information of the master event [known]
master = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
# Information of the slave event [to be relocated]
slave = Event("1995-11-14T06:32:55.750", -3.682, 101.924, 57.0, 5.1)

# observation file
obsfile = "obs-2003-1995.dat"

# search parameters
"""
sol_type = "geographic"  # dlat, dlon and ddepth
ranges = (
    slice(-0.01, 0.01, 0.0005),  # dlat in degree
    slice(-0.01, 0.01, 0.0005),  # dlon in degree
    slice(-1, 1, 0.2),  # ddepth in km
)
"""
sol_type = "cylindrical"  # ddist, azimuth, and ddepth
ranges = (
    slice(0, 1000, 10),  # ddist in meter
    slice(0, 360, 5),  # az in degree
    slice(-1000, 1000, 20),  # ddepth in meter
)

print("Ex2 for ddrelocator")
print("Master event: ", master)
print("Slave event: ", slave)

# read observations from a file
obslist = read_obslist(obsfile)
print(f"Read {len(obslist)} observations from {obsfile}")

# visualize the observations
plot_dt(obslist, master)

# relocate the slave event relative to the master event
print("Grid search...  ", end="")
start = time.time()
sol, grid, Jout = find_solution(master, obslist, ranges, sol_type)
print(f"Done in {time.time() - start:.1f} sec")

# Try the best solution again to add more properties like tmean and residuals
try_solution(master, obslist, sol, keep_residual=True)
# the best location for the slave event
slave_sol = sol.to_event(master, slave)
print("Best solution:", sol)
print("Slave event: ", slave_sol)

# visualize the residuals
plot_residual(obslist, master, slave_sol)

# visualize the misfit
plot_misfit(grid, Jout, sol_type)

# Save the solutions into a pickle file so it can be reused
dump_solutions(grid, Jout, "solutions.pkl")
