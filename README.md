# Metabolic syndrome early-risk group (caution group) at health screening across districts of South Korea, 2019-2024

Analysis code for the manuscript

> Kim S. *Early Metabolic Risk Is Modestly Higher in Less-Educated Districts of South Korea.*

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24391134 (v1.1.0).

This code is released under the MIT licence.

## Contents

This repository contains code only. The processed district-year data (analytic panel, expected counts, result tables and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/MSPRE/` | Covariate pool and model settings (`make_pool_sets_mspre.py`, `sets_MSPRE_*.json`, `config_MSPRE_*.json`), input audits (`gate_sqlite_crosscheck_mspre.py`, `gate_zero_year_audit_mspre.py`), the full model chain (`run_chain.sh`) and the district adjacency graph (`graph_593.graph`). Versions: principal `main`; refit `r2`; queen contiguity graph `s577`; covariate set S2 `s2`; crude expected counts `sc`; population-based expected counts `sp`; earlier lipid-testing schedule 2013-2017 `aux` |
| `04_분석/MSPRE/MS/build/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supporting information (`numbers_mspre.py`, `labels_mspre.py`, `figs_mspre.py`, `content_mspre.py`, `build_manuscript_mspre.py`, `esm_mspre.py`, `build_refs_mspre.py`) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Examinees with one or two metabolic syndrome components (caution group) and examinees assessed for metabolic risk components, by district and sex: National Health Insurance Service screening statistics, KOSIS tables DT_35007_N135 and DT_35007_N138, 2013-2024.
- National examinees, caution group and component prevalences by sex and age: KOSIS DT_35007_N136 and DT_35007_N139.
- Population by sex and 5-year age group: Ministry of the Interior and Safety, resident registration statistics.
- District covariates: Community Health Survey (nutrition label use, weight control attempts, perceived stress, depressive mood, obesity, high-risk drinking, current smoking), population and housing census (tertiary education, single-person households), public assistance statistics, screening attendance and KOSIS local indicators (fixed adjustments and negative controls).

## Pipeline

Set `ST_DATA_ROOT` and `ST_GPT_DATASET` to the local copies of the public source files and the read-only district database, then run from the repository root.

| Step | Script | Output |
|---|---|---|
| 1 | `99MP1_mspre_judgement_gate.py` | Composition check of the outcome by year (national, provincial, district) |
| 2 | `99MP2_build_Estd3_mspre.py` | District caution-group counts and expected counts by indirect standardisation in 2 sexes x 15 age groups (2019-2024 and 2013-2017) |
| 3 | `99c_extra_canonical_pool_digx.py`, `99c_extra_canonical_pool_lipt.py`, then `04_분석/MSPRE/make_pool_sets_mspre.py` | Covariate pool and model settings (hashed before fitting); comparison outcomes |
| 4 | `80_build_disease_panel_v.py MSPRE` (`ST_VER=main`) | Analytic panel |
| 5 | `04_분석/MSPRE/run_chain.sh` (wraps R jobs in `rslot.sh`) | Principal model, 200-subset multiverse, period models, sensitivity versions, maps, alternative specifications, Knorr-Held models, restricted spatial regression, comparison outcomes |
| 6 | `04_분석/MSPRE/MS/build/` | Manuscript numbers, tables, figures and supporting information |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19 (one thread), spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, matplotlib and python-docx.

## Licence

MIT (see `LICENSE`).
