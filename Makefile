VENV_NAME := venv
ACTIVATE_VENV := . $(VENV_NAME)/bin/activate
PYTHON := $(VENV_NAME)/bin/python3
PIP := $(VENV_NAME)/bin/pip

.PHONY: all venv run clean

all: run

venv: requirements.txt
	python3 -m venv $(VENV_NAME)
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

run: venv
	$(PYTHON) main.py

clean:
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
	rm -rf $(VENV_NAME) *.spec
