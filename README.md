# precog-data-intake 🦑

Data sweep and scraping utilities for downloading and organizing Earth system data from Earth System Grid Federation (ESGF) nodes based on core functionality from [esgf-intake](https://intake-esgf.readthedocs.io/en/latest/)

## Overview

This repository contains scripts and workflows to automate bulk discovery, file checking, validation and download of datasets from ESGF archives.
It is designed to support climate and oceanographic analyses that require consistent, reproducible access to large model and observational datasets.

## Features

- Automated search through the ESGF catalogue using project, variable, experiment, and temporal filters.
- Verification of continuity in CMIP6 Pre-Industrial and Historical runs
- Batched download of files from multiple ESGF nodes with retry and integrity checks.
- Local directory layout optimized for downstream analysis tools.
- Batched search and download of grid cell measures (e.g., 'areacello' and 'volcello') with archive snapshot of relaxed regex matches for CMIP6 models of interest.

## Installation

These instructions assume you have **Python 3.12+** installed and available as `python` or `python3` on your system.

### 1. Clone the repository

```bash
git clone https://github.com/LeoBertini/precog-data-intake.git
cd precog-data-intake
````
### 2. Create a virtual environment (named .venv)
```bash
python3.12 -m venv .venv
````
Make sure your python version is >3.12.
the '.venv' means a virtual environment called 'venv' will be created with its dependencies put in a hidden system folder called '.venv' under the project directory you are in (i.e., ~/precog-data-intake)

### 3. Activate it
```bash
source .venv/bin/activate
```
When activation succeeds, your shell prompt will usually show the environment name in parentheses, for example: `(.venv) ...`

### 4. Upgrade pip (recommended)
Inside the activated virtual environment, upgrade `pip`:
```bash
python -m pip install --upgrade pip
```
### 5. Install dependencies
```bash 
pip install -r requirements.txt
```

## Repository structure
```                

precog-data-intake/
├─.venv/                 # Hidden folder with virtual enviroment dependencies               
├─ intake_esgf_mods/     # Modified Python modules from the main package "esgf-intake"
├─ misc_images/          # Images (these are renderered as ASCII art headers and footers in cli)
├─ scripts/              # Workflows as command line scripts
├─ notebooks/            # Example notebooks of usage
└─ tests/                # Basic tests for core functionality
```
