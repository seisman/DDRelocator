# Build, package, test and clean
PROJECT=ddrelocator
FORMAT_FILES=${PROJECT} examples

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
	ruff check ${FORMAT_FILES}
	ruff format --check ${FORMAT_FILES}

format:
	ruff check --fix --exit-zero ${FORMAT_FILES}
	ruff format ${FORMAT_FILES}

clean:
	find . -name "*.pyc" -exec rm -v {} +
	find . -name "*~" -exec rm -v {} +
	find . -type d -name  "__pycache__" -exec rm -rv {} +
	rm -rf .ruff_cache

distclean: clean
	rm -rvf *.egg-info
