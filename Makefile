# Build, package, test and clean
PROJECT=ddrelocator

help:
	@echo "Commands:"
	@echo ""
	@echo "  install      install in editable mode"
	@echo "  check        check the code for errors"
	@echo "  format       format the code automatically"
	@echo "  clean        clean up build and generated files"
	@echo "  distclean    clean up build and generated files, including project metadata files"
	@echo ""

install:
	python -m pip install --no-deps -e .

check:
	ruff check ${PROJECT} examples
	ruff format --check ${PROJECT} examples

format:
	ruff check --fix ${PROJECT} examples
	ruff format ${PROJECT} examples

clean:
	find . -name "*.pyc" -exec rm -v {} +
	find . -name "*~" -exec rm -v {} +
	find . -type d -name  "__pycache__" -exec rm -rv {} +
	rm -r .ruff_cache

distclean: clean
	rm -rvf *.egg-info
