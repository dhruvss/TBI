# Round 3 Error Correction and Recomputed Outputs

This folder contains error logs, corrected files, and recomputed CSV outputs related to quality-control checks from the later enumeration and screening stages.

During lead candidate review, several analogs were found to contain SMILES duplication, mismatched modification labels, or parsing issues involving CF and CF2 group modifications. These errors affected calculated molecular weight, estimated lipophilicity, CNS-MPO scoring, and downstream lead selection.

Affected analogs were corrected, redocked or recomputed where appropriate, and then re-evaluated under the same CNS-MPO and screening criteria. Candidates that failed corrected physicochemical or scoring thresholds were excluded from final PBPK analysis but retained in the dataset for transparency.

Files in this folder may include:
- Original error logs
- Recomputed error logs
- Corrected candidate CSVs
- Exclusion/QC documentation

This folder supports reproducibility of the final lead set and documents why certain candidates were excluded from the final 17-candidate PBPK analysis.
