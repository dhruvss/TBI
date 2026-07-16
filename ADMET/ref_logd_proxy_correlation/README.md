# Reference tracer logD7.4 proxy benchmark

This folder benchmarks the polarity-adjusted lipophilicity proxy used for analog triage:

logD7.4_EST = computed logP - TPSA / 120

The proxy was compared against six reference TSPO tracers with reported experimental logD7.4 values: PK11195, DPA-713, PBR-28, GE-180, AC-5216, and PBR-O6. PBR-111 and DAA1106 were excluded from correlation analysis because experimental logD7.4 values were unavailable in the curated reference table.

## Summary

PubChem XLogP showed strong concordance with experimental logD7.4 values:

- Pearson r = 0.886
- Spearman r = 0.657
- MAE = 0.567

The PubChem XLogP - TPSA/120 proxy retained similar correlation while reducing absolute error:

- Pearson r = 0.870
- Spearman r = 0.657
- MAE = 0.363

The RDKit clogP - TPSA/120 implementation showed more moderate but directionally consistent performance:

- Pearson r = 0.735
- Spearman r = 0.657
- MAE = 0.729

A sensitivity analysis excluding DPA-713 produced similar trends, indicating that the result was not dependent on that tracer.

## Interpretation

The polarity-adjusted lipophilicity proxy is suitable as a screening-level relative triage descriptor. It should not be interpreted as a validated replacement for experimental shake-flask logD7.4 measurement. AC-5216 was notably underpredicted by both proxy implementations, reinforcing the need for conservative interpretation.
