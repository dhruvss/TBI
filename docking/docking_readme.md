# Docking data

This directory contains the curated docking inputs, reference tracer structures,
final docking outputs, error-correction records, and summary tables used in the study.

The complete generated analog workspaces for:

- `emap_enum_round1/`
- `emap_enum_round2/`
- `emap_enum_round3/`

are intentionally excluded because they contain thousands of reproducible intermediate
files, including generated SDF/PDBQT structures, docking poses, and logs.

The full analog library is retained in machine-readable form in:

- `all_rounds_smiles.csv`
- `round12_CNS.csv`
- downstream master statistics and processed supplement tables

Each analog is identified by compound ID and SMILES, allowing the omitted structure
files to be regenerated using the scripts in `src/`.

The public repository therefore includes the chemically defining structures,
docking parameters, selected outputs, summary statistics, and code required to
reconstruct the reported workflow without storing thousands of redundant intermediate files.
