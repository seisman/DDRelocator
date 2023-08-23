# Build, package, test and clean
PROJECT=ddrelocator

help:
	@echo "Commands:"
	@echo ""
	@echo "  install      install in editable mode"
	@echo "  format       format the code automatically"
	@echo "  lint         lint the code"
	@echo "  clean        clean up build and generated files"
	@echo "  distclean    clean up build and generated files, including project metadata files"
	@echo ""

install:
	python -m pip install --no-deps -e .

format:
	isort .
	black .

lint:
	pylint ${PROJECT} examples

clean:
	find . -name "*.pyc" -exec rm -v {} +
	find . -name "*~" -exec rm -v {} +
	find . -type d -name  "__pycache__" -exec rm -rv {} +

distclean:
	rm -rvf *.egg-info
