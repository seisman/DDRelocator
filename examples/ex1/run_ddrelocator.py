"""
A sythetic test for ddrelocator.
"""
import numpy as np
from ddrelocator.ddrelocator import find_best_solution, gridsearch, try_solution
from ddrelocator.headers import Event, SearchParams, Solution
from ddrelocator.helpers import read_obslist
from ddrelocator.plotting import plot_dt, plot_residual

# Information of the master event [known]
master = Event("2018-02-01T00:00:00", 36.1688, 139.8075, 53.45, 4.7)
# Information of the slave event [unknown]
slave = Event("2018-02-02T00:00:00", 36.1678, 139.8095, 53.45, 4.7)

# read observations from a file
obslist = read_obslist("obs.dat")

# search parameters
params = SearchParams(
    dlats=np.arange(-0.05, 0.05, 0.001),
    dlons=np.arange(-0.05, 0.05, 0.001),
    ddeps=np.arange(-2, 2, 1.0),
)

print("Ex1 for ddrelocator")
print(f"Master event: {master.latitude:.5f} {master.longitude:.5f} {master.depth:.2f}")
print(f"Slave event: {slave.latitude:.5f} {slave.longitude:.5f} {slave.depth:.2f}")

# visualize the observations
plot_dt(obslist, master, show_unused=True)

# relocate the slave event relative to the master event
# 1. Grid search to find the best solution
print("Grid search...")
solutions = gridsearch(master, obslist, params)
sol = find_best_solution(solutions)
# 2. Just try a solution
# sol = Solution(-0.001, 0.002, 0.0, master)

print(
    f"Best solution: {sol.latitude:.5f} {sol.longitude:.5f} {sol.depth:.2f} {sol.tmean:.3g}"
)
print(f"Misfit: {sol.misfit:.3g}")

# Call the try_solution function again to update the residuals saved in obs
try_solution(obslist, sol)

plot_residual(obslist, master, slave)
