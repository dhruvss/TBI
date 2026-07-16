# Reference tracer logD proxy check

Quick check of the polarity-adjusted lipophilicity proxy used in the analog triage:

logD7.4_EST = computed logP - TPSA / 120

This was not meant to be a perfect logD predictor. It was a rough screening descriptor to keep analog ranking from depending only on raw logP.

## What was checked

I compared the proxy against the reference TSPO tracers where I had literature logD7.4 values:

- PK11195
- DPA-713
- PBR-28
- GE-180
- AC-5216 / emapunil
- PBR-O6

PBR-111 and DAA1106 were not included in the correlation because I did not have usable logD7.4 values for them in the curated reference table.

For emapunil / AC-5216, I used the clinical-standard literature value used throughout the project.

## Main result

The proxy behaved reasonably, but it is still only a rough triage metric.

PubChem XLogP alone:

- Pearson r = 0.886
- Spearman r = 0.657
- MAE = 0.567

PubChem XLogP - TPSA/120:

- Pearson r = 0.870
- Spearman r = 0.657
- MAE = 0.363

RDKit clogP - TPSA/120:

- Pearson r = 0.735
- Spearman r = 0.657
- MAE = 0.729

So the polarity correction did not improve every metric, but it did reduce absolute error for the PubChem implementation and kept the same general trend.

## DPA-713 note

DPA-713 was kept in the main analysis. The logD value is supported by Owen et al.; the only caveat is that one secondary supporting source used extrapolation. I also ran a sensitivity check without DPA-713, and the overall trend was similar.

## Interpretation

This proxy is good enough for rough analog triage.

It should not be described as experimentally validated, and it should not replace measured shake-flask logD7.4. It is just a quick polarity-adjusted lipophilicity screen for compounds where experimental logD does not exist yet.
