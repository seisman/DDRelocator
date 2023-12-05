"""
ex1: Run ddrelocator.
"""
import time

from ddrelocator import Event, SearchParams, find_solution, try_solution
from ddrelocator.helpers import dump_solutions, read_obslist
from ddrelocator.plotting import plot_dt, plot_misfit, plot_residual

# Information of the master event [known]
master = Event("2018-02-01T00:00:00", 36.1688, 139.8075, 53.45, 4.7)
# Information of the slave event [unknown]
slave = Event("2018-02-02T00:00:00", 36.1678, 139.8095, 53.45, 4.7)

# observation file
obsfile = "obs.dat"

# search parameters
params = SearchParams(
    dlats=slice(-0.002, 0.002, 0.0002),
    dlons=slice(-0.004, 0.004, 0.0002),
    ddeps=slice(-1, 1, 0.01),
)

print("Ex1 for ddrelocator")
print("Master event: ", master)
print("Slave event: ", slave)

# read observations from a file
obslist = read_obslist(obsfile)
print(f"Read {len(obslist)} observations from {obsfile}")

# visualize the observations
plot_dt(obslist, master, show_unused=True)

# relocate the slave event relative to the master event
print("Grid search...  ", end="")
start = time.time()
sol, grid, Jout = find_solution(master, obslist, params)
print(f"Done in {time.time() - start:.1f} sec")

# Try the best solution again to add more properties like tmean and residuals
try_solution(obslist, sol, keep_residual=True)
# the best location for the slave event
slave_sol = Event(
    slave.origin + sol.tmean, sol.latitude, sol.longitude, sol.depth, slave.magnitude
)
print("Best solution:", sol)
print("Slave event: ", slave_sol)

# visualize the residuals
plot_residual(obslist, master, slave_sol)

# visualize the misfit
plot_misfit(grid, Jout)

# Save the solutions into a pickle file so it can be reused
dump_solutions(grid, Jout, "solutions.pkl")
