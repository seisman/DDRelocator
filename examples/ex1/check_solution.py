"""
ex1: Check a solution.

The solution can be the best solution from gridsearch or any other solution.
"""
from ddrelocator import Event, Solution, try_solution
from ddrelocator.helpers import read_obslist
from ddrelocator.plotting import plot_residual

master = Event("2018-02-01T00:00:00", 36.1688, 139.8075, 53.45, 4.7)
slave = Event("2018-02-02T00:00:00", 36.1678, 139.8095, 53.45, 4.7)

# The solution to check.
# It can be the best solution from gridsearch or any other solution.
sol = Solution((-0.001, 0.002, 0.0), type="geographic")

# read observations from a file
obslist = read_obslist("obs.dat")

# Call the try_solution function with the given solution and keep predicted
# traveltime difference and residual in obs.
try_solution(master, obslist, sol, keep_residual=True)
slave_sol = sol.to_event(master, slave)

# visualize the residuals
plot_residual(obslist, master, slave_sol)
