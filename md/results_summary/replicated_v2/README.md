# Replicated MD analysis

The checked-in trajectory tables and statistical outputs in this directory
contain the finalized five-replicate analysis: five independent 10 ns trajectories
for each of A3, A7, A8, A15, and AC-5216, yielding 25 trajectories in total.

The authoritative workflow requires exactly five independent 10 ns trajectories
for each of A3, A7, A8, A15, and AC-5216. It fails before writing outputs if the
complete 5 x 5 design or frame-level validation is not satisfied.

To regenerate the outputs from the locally retained per-trajectory analyses,
run from the repository root:

```bash
python md/scripts/aggregate_md_reps.py
python md/scripts/analyze_md_replicate_statistics.py
```

Only the three prespecified primary endpoints receive exploratory inference.
Secondary endpoints are descriptive only. The primary figure shows trajectory
values and mean +/- SD without significance annotations.
