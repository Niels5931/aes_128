TARGET?=$(PROJECT_NAME)
VENV_NAME?=_env
SHELL := /bin/bash

setup:
	echo "Setting up environment for project $(basename "$(PWD)")"
	echo "source $(PWD)/$(VENV_NAME)/bin/activate" >> source_simpl
	python3 -m venv $(VENV_NAME)/
	source $(VENV_NAME)/bin/activate && \
	pip install --upgrade pip && \
	pip install cocotb pyuvm pytest

sim:
	echo "Running simulation of $(TARGET)"
	cd cores/$(TARGET)/sim && simpl xsim

build:
	source source_simpl
	echo "Building $(TARGET)"
	cd cores/$(TARGET)/syn && simpl vivado

project:
	echo "Creating project for $(TARGET)"
	make_project.py $(TARGET)
	cd cores/$(TARGET)/_project/ && vivado -mode tcl -source project.tcl
	cd cores/$(TARGET)/_project/ && vivado project.xpr

open:
	cd cores/$(TARGET)/_project/ && vivado project.xpr

check_syntax:
	source source_simpl && check_syntax.py $(TARGET)

clean:
	@rm -rf cores/* 
