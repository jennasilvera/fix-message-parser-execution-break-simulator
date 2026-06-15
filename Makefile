PYTHONPATH := src

.PHONY: setup generate parse load reconcile test run clean

setup:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

generate:
	PYTHONPATH=$(PYTHONPATH) python -m fixops.generate_sample_data

parse:
	PYTHONPATH=$(PYTHONPATH) python -m fixops.fix_parser

load:
	PYTHONPATH=$(PYTHONPATH) python -m fixops.load_db

reconcile:
	PYTHONPATH=$(PYTHONPATH) python -m fixops.reconcile

test:
	pytest

run: generate parse load reconcile

clean:
	rm -f db/*.db
	rm -f data/generated/*.csv
	rm -f reports/exceptions/*.csv
