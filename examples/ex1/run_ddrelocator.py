"""
ex1: Run ddrelocator.
"""
import time

import numpy as np
from ddrelocator import Event, SearchParams, find_best_solution, gridsearch
from ddrelocator.helpers import dump_solutions, read_obslist
from ddrelocator.plotting import plot_dt

# Information of the master event [known]
master = Event("2018-02-01T00:00:00", 36.1688, 139.8075, 53.45, 4.7)
# Information of the slave event [unknown]
slave = Event("2018-02-02T00:00:00", 36.1678, 139.8095, 53.45, 4.7)

# read observations from a file
obslist = read_obslist("obs.dat")

# search parameters
params = SearchParams(
    dlats=np.arange(-0.02, 0.02, 0.001),
    dlons=np.arange(-0.02, 0.02, 0.001),
    ddeps=np.arange(-2, 2, 0.1),
)

print("Ex1 for ddrelocator")
print(f"Master event: {master.latitude:.5f} {master.longitude:.5f} {master.depth:.2f}")
print(f"Slave event: {slave.latitude:.5f} {slave.longitude:.5f} {slave.depth:.2f}")

# visualize the observations
plot_dt(obslist, master, show_unused=True)

# relocate the slave event relative to the master event
print("Grid search...  ", end="")
start = time.time()
solutions = gridsearch(master, obslist, params)
print(f"Done in {time.time() - start:.1f} sec")
sol = find_best_solution(solutions)

print(
    "Best solution:\n"
    f"latitude: {sol.latitude:.5f}\n"
    f"longitude: {sol.longitude:.5f}\n"
    f"depth: {sol.depth:.2f}\n"
    f"time: {sol.tmean:.3g}\n"
)
print(f"Misfit: {sol.misfit:.3g}")

dump_solutions(solutions, "solutions.pkl")
