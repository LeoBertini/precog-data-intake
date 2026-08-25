---
title: "precog-data-intake: Tolls for automating bulk discovery, file checking, validation and download of Earth System Model archives across Earth System Federation nodes"
tags:
  - Python
  - Earth System Modelling
  - Biogeochemical Cycles
  - Earth Sciences
authors:
  - name: Leonardo Bertini^[corresponding author]
    orcid: 0000-0003-3920-4476
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Jamie Wilson
    orcid:
    affiliation: 1
  - name: Sam Ditkovsky
    orcid:
    affiliation: 1
affiliations:
  - name: Department of Earth, Ocean and Ecological Sciences, University of Liverpool, UK
    index: 1
date: 11 Feb 2026
bibliography: paper.bib
---

# Summary

`precog-data-intake` is a Python command-line-interface (CLI) software for automated discovery, checking,
validation, and download of Earth System Model outputs from Earth System Grid Federation (ESGF) archives. The
software is designed for research workflows that require reproducible access to large, distributed climate-model
datasets and is particularly aimed at bulk screening of Earth system archives before downstream analysis. The
software builds on inherited ESGF access functionality from `intake-esgf` [@Collier_intake_esgf_2026], while
introducing interactive CLI workflows for archive interrogation, file-availability checks, grid-consistency
cross-checks, temporal validation, export of search-result in tabular formats, and download management of shortlisted
Earth System Model data products.

# Statement of need

Modern Earth system science workflows frequently rely on climate-model data distributed across ESGF nodes.
Although ESGF provides a federated infrastructure for searching and accessing these archives, practical
research workflows often require additional automation to determine whether a given combination of variables,
experiments, ensemble members, and grid configurations is both scientifically suitable and operationally downloadable
before substantial time is spent retrieving files.

This issue is especially important for CMIP6-style analyses in which researchers may need to confirm that the same
model provides paired pre-industrial, historical and ssp-scenario simulations, that multiple variables of interest are
available on compatible grids for downstream analyses, and that temporal coverage is continuous across archived files.
Manual inspection of catalogue search results can become slow, repetitive, and error-prone when screening many candidate
models or variables across multiple ESGF nodes.

`intake-esgf` provides an important upstream foundation for this work by enabling access to information on ESGF
nodes [@Collier_intake_esgf_2026]. `precog-data-intake` builds on that core implementation but targets a different level
of the workflow: rather than focusing only on data access primitives and caching to in-memory use, it provides an
interactive command-line environment for ample discovery, screening, validating and managing downloads of published ESGF
archive products that satisfy scientific constraints relevant to Earth system and ocean biogeochemistry applications.
The software is intended for situations in which researchers need to move efficiently from broad catalogue searches to a
smaller, analysis-ready subset of model output that satisfies practical and scientific constraints.

Therefore, `precog-data-intake` fills a workflow gap between catalogue access and scientific analysis. It helps users
shortlist Earth System Models that satisfy compound criteria across experiments and variables, validate archive
consistency before download, export tabular summaries of search results, identify datasets that are actually
downloadable, and organize retrieved files into a local directory structure suited to reproducible downstream
analysis. This design is particularly useful when users need to screen many candidate models and variables before
deciding which datasets are scientifically suitable and operationally downloadable.

# Key functionality

The software provides several features tailored to archive-scale Earth system data workflows:

- automated ESGF searches using project, activity, experiment, frequency, variable, and grid filters
  (inherited from `intake-esgf`);
- interactive user prompts for download paths and variable selections within CLI workflows;
- bulk screening of CMIP6 archive holdings for paired `piControl` and `historical` availability;
- validation of continuity in date stamps for CMIP6 pre-industrial and historical simulations;
- checks for consistent availability of model output across compatible grids such as `gn` and `gr`;
- conditional multi-variable screening for models that satisfy compound search criteria, including cases where several
  required variables must be available simultaneously;
- export of tabular ESGF catalogue search results for easy inspection, logging, and reproducible shortlist generation;
- parallel URL pre-checks with verification of server responses and flagging of shortlisted outputs as downloadable;
- download manager with parallel transfers that select responsive ESGF node locations and include retry or integrity
  checks for corrupted files
- retrieval of ocean grid-cell measure variables such as `areacello` and `volcello` for selected models, together with
  saved archive snapshots for later inspection.

These capabilities support workflows in which data access is itself a significant part of the scientific process,
particularly when analyses depend on assembling coherent, scientifically consistent, and analysis-ready
ensemble subsets of Earth system model output from distributed archives.

# Research applications

A representative use case is the identification of CMIP6 models that simultaneously provide both pre-industrial
and historical output for ocean biogeochemical variables such as `expc` and `epc100`, together with auxiliary or
supporting variables and the associated grid-cell measures required for downstream calculations. The repository
includes workflows and notebooks demonstrating this type of archive screening and retrieval
process [notebooks](../notebooks).

This is particularly relevant for ocean biogeochemistry and carbon-cycle studies, where analyses often depend on
coherent combinations of physical and biogeochemical fields rather than isolated variables (e.g., retrieval of
carbonate system fields as well as ocean state physical variables). In such cases, the time spent screening archive
holdings, checking consistency, and organizing downloads can be substantial, and purpose-built automation improves both
efficiency and reproducibility.

# Acknowledgements

This work is part of the [PRECOG - Predicting Biological Carbon in the Ocean Globally](https://precog-ocean.github.io)
project, funded by UK Research and Innovation (UKRI) through a Future Leaders Fellowship Award (Project Reference
MR/Y016629/1). `precog-data-intake` builds directly on the core implementation by `intake-esgf`, and this dependency is
gratefully acknowledged [@Collier_intake_esgf_2026]. The authors thank the developers of `intake-esgf` and the wider
ESGF infrastructure for making climate-model archives programmatically accessible to the research community.

# References

