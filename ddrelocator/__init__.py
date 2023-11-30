"""
ddrelocator
===========

A Python package for determining the relative location of two nearby earthquakes
using the master-event algorithm.
"""
from ddrelocator.headers import Event, Obs, SearchParams, Solution, Station
from ddrelocator.locator import gridsearch, try_solution
