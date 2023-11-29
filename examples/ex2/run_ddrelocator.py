"""
ex2: Run ddrelocator.
"""
import time

import numpy as np
from ddrelocator import Event, SearchParams, find_best_solution, gridsearch
from ddrelocator.helpers import dump_solutions, read_obslist
from ddrelocator.plotting import plot_dt

obslist = read_obslist("obs-2003-1995.dat")

master = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
plot_dt(obslist, master)

params = SearchParams(
    dlats=np.arange(-0.01, 0.01, 0.0005),
    dlons=np.arange(-0.01, 0.01, 0.0005),
    ddeps=np.arange(-1, 1, 0.2),
)

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
dump_solutions(solutions, "solutions.pkl")
