# Replicated MD analysis

The checked-in trajectory tables in this directory are interim three-replicate
data and are not the final inferential analysis. Obsolete three-replicate test
outputs were removed to prevent accidental publication or interpretation.

The authoritative workflow requires exactly five independent 10 ns trajectories
for each of A3, A7, A8, A15, and AC-5216. It fails before writing outputs if the
complete 5 x 5 design or frame-level validation is not satisfied.

Run, after all 25 trajectories have been analyzed:

```bash
python md/scripts/aggregate_md_reps.py
python md/scripts/analyze_md_replicate_statistics.py
```

Only the three prespecified primary endpoints receive exploratory inference.
Secondary endpoints are descriptive only. The primary figure shows trajectory
values and mean +/- SD without significance annotations.
