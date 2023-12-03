"""
ex2: Run ddrelocator.
"""
import time

from ddrelocator import Event, SearchParams, gridsearch, try_solution
from ddrelocator.helpers import dump_solutions, read_obslist
from ddrelocator.plotting import plot_dt, plot_misfit, plot_residual

# Information of the master event [known]
master = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
# Information of the slave event [to be relocated]
slave = Event("1995-11-14T06:32:55.750", -3.682, 101.924, 57.0, 5.1)

# observation file
obsfile = "obs-2003-1995.dat"

# search parameters
params = SearchParams(
    dlats=slice(-0.01, 0.01, 0.0005),
    dlons=slice(-0.01, 0.01, 0.0005),
    ddeps=slice(-1, 1, 0.2),
)

print("Ex2 for ddrelocator")
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
sol, grid, Jout = gridsearch(master, obslist, params)
print(f"Done in {time.time() - start:.1f} sec")

# Try the best solution again to add more properties like tmean and residuals
try_solution(obslist, sol, keep_residual=True)
# the best location for the slave event
slave_sol = Event(
    slave.origin + sol.tmean, sol.latitude, sol.longitude, sol.depth, slave.magnitude
)
print(
    "Best solution:\n"
    f"dlat: {sol.dlat:.5f}\n"
    f"dlon: {sol.dlon:.5f}\n"
    f"ddepth: {sol.ddepth:.2f}\n"
    f"tmean: {sol.tmean:.3g}\n"
    f"misfit: {sol.misfit:.3g}"
)
print("Slave event: ", slave_sol)

# visualize the residuals
plot_residual(obslist, master, slave_sol)

# visualize the misfit
plot_misfit(grid, Jout)

# Save the solutions into a pickle file so it can be reused
dump_solutions(grid, Jout, "solutions.pkl")
