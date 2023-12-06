"""
ddrelocator
===========

A Python package for determining the relative location of two nearby earthquakes
using the master-event algorithm.
"""
from ddrelocator.headers import Event, Obs, Solution, Station
from ddrelocator.locator import find_solution, try_solution
