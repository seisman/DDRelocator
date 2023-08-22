import pandas as pd
import numpy as np
from ddrelocator.ddrelocator import (
    Event,
    Obs,
    SearchParams,
    find_best_solution,
    gridsearch,
)
from ddrelocator.helpers import read_obslist
from ddrelocator.plotting import plot_dt, plot_residual

obslist = read_obslist("obs-2003-1995.txt")

master = Event("2003-07-02T00:47:11.860", -3.643, 102.060, 75.2, 5.1)
plot_dt(obslist, master)

params = SearchParams(
    dlats=np.arange(-0.01, 0.01, 0.0005),
    dlons=np.arange(-0.01, 0.01, 0.0005),
    ddeps=np.arange(-1, 1, 0.2),
)

solutions = gridsearch(master, obslist, params)
sol = find_best_solution(solutions)
print(
    f"Best solution: {sol.latitude:.5f} {sol.longitude:.5f} {sol.depth:.2f} {sol.tmean:.3g}"
)
