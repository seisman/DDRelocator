"""
Check the misfit as a function of longitude, latitude and depth.
"""
from ddrelocator.helpers import load_solutions
from ddrelocator.locator import find_best_solution
from ddrelocator.plotting import plot_misfit

solutions = load_solutions("solutions.pkl")
bestsol = find_best_solution(solutions)
plot_misfit(solutions, bestsol)
