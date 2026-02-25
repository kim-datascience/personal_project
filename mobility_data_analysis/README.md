# Project Summary

The data files are from two mobility companies, Company A and Company B. We are interested in learning more about the
dynamics of the market in which they operate.

This project demonstrates data science work on mobility data from raw data exploration to business recommendations.

**operation_description.ipynb (Main)** — Operational comparison and recommendations. Compares two mobility companies across time, defines geography clusters (Downtown, University, Residential), and usage patterns.

**eda.ipynb** — Exploratory data analysis. Infers data structure and units (e.g., infers the distance unit is in miles through latitude/longitude coordinate comparison), identifies and removes invalid records (outliers, unphysical distances or durations), and validates cleaning choices. Documents the reasoning behind each data preprocessing step.

**estimate_num_scooter_company_b.ipynb** — Fleet size estimation of Company B. Suggested three approaches presenting estimates under each assumption.

* preprocess_data.py: Load and clean data, and generate data frames for above notebooks

* plot_utils.py: Plot util functions used by operation_description.ipynb

* data: mobility data (not included here)

* fig: a map figure used by operation_description.ipynb