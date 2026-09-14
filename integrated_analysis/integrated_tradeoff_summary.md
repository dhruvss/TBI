# Integrated TSPO candidate analysis

Pareto-optimal candidates are **A7 and AC-5216**. **A7 dominates A3, A8 and A15**; these are the only domination relationships. AC-5216 dominates none and remains nondominated because it has the lowest mean COM distance.

Dominance uses the full stored precision of four objectives only: maximize the existing PBPK Final_Weighted_Score, MD mean fixed-pocket contacts and mean percentage of frames with ≥10 contacts; minimize MD mean COM-to-fixed-pocket-center distance. X dominates Y only when at least as good on all four and strictly better on at least one. SDs and feasibility annotations do not enter dominance. This is descriptive dominance of point estimates, not an inferential superiority claim.

| Candidate | PBPK score | PBPK rank* | Contacts, mean ± SD | COM, Å, mean ± SD | ≥10 contacts, %, mean ± SD |
|---|---:|---:|---:|---:|---:|
| A3 | 0.6761 | 2 | 11.57 ± 6.20 | 8.86 ± 1.69 | 54.08 ± 28.75 |
| A7 | 1.4419 | 1 | 28.25 ± 5.94 | 6.65 ± 1.08 | 97.96 ± 2.04 |
| A8 | 0.3447 | 7 | 16.64 ± 3.04 | 6.98 ± 0.96 | 85.76 ± 8.26 |
| A15 | 0.3031 | 8 | 17.04 ± 3.31 | 8.30 ± 0.83 | 82.14 ± 9.51 |
| AC-5216 | -2.0131 | Reference | 18.49 ± 2.19 | 6.56 ± 0.86 | 87.98 ± 9.15 |

*PBPK ranks are copied from the finalized baseline ranking of 17 analog records (A3=2, A7=1, A8=7, A15=8), not reranked among these five candidates. AC-5216 is excluded from that source ranking, so its CSV rank is blank. MD values are finalized trajectory-level mean ± SD, n=5 per candidate; occupancy remains in percentage units. CSVs preserve stored numeric precision.

- **A7:** The performance-maximizing analog across all four objectives, and the five-candidate leader in PBPK, contacts and occupancy. It is not a universal four-objective maximum: AC-5216 has a slightly shorter mean COM distance (6.565 versus 6.647 Å). A7 has nonsupportive BBB consensus, discordant P-gp predictions and a predicted hERG II flag. ASKCOS recovered zero complete routes, no buyable-terminal route, and classifies it as “plausible route with one unresolved key step”: preparation of the N-difluoromethylated purinone core.
- **A8:** A plausible qualitative performance–feasibility compromise among the analogs: supportive BBB consensus and 200 complete buyable-terminal routes, with strong scaffold precedent. It cannot be established as uniquely “most balanced” without preference weights: A7 dominates it quantitatively, and A8 retains predicted Ames/hERG II flags and duplicate-run Ames disagreement. Its PBPK exceeds AC-5216, while all three MD means are less favorable. Relative to A15 it has better PBPK, COM and occupancy but slightly fewer contacts. Its bulky alpha-bromoamide/purinone N-alkylation and advanced precursor availability need confirmation.
- **A3:** Replicated MD weakens its strong PBPK position descriptively: lowest contacts and occupancy, greatest COM distance and largest SDs on all three endpoints. Its PBPK exceeds AC-5216, while all MD means are less favorable. A7 dominates it. BBB predictions are discordant, with a hERG II flag and discordant P-gp predictions; 200 complete buyable-terminal routes recover strong scaffold precedent, with N-trifluoroethylation reactivity/regioselectivity unresolved.
- **A15:** Dominated by A7; it offers no distinct nondominated quantitative advantage. It has slightly more contacts than A8 and no predicted Ames flag in its finalized profile, alongside 200 complete buyable-terminal routes and strong scaffold precedent. Its PBPK exceeds AC-5216, while all MD means are less favorable. BBB consensus is nonsupportive, P-gp predictions discordant and hERG II flagged. Exact substituted benzyl-halide access and secondary-amine monoalkylation versus overalkylation remain uncertainties.
- **AC-5216:** Lowest PBPK score but shortest mean COM distance; more contacts and occupancy than A3, A8 and A15, and fewer than A7. It has supportive BBB consensus, discordant P-gp predictions, predicted Ames/hERG II flags, and 200 complete buyable-terminal routes with strong scaffold precedent. Advanced purinone access and haloacetate N-alkylation selectivity still need confirmation.

All five finalized ADMET profiles have no predicted hERG I or hepatotoxicity flag and zero PAINS/Brenk alerts. A8 duplicate runs disagree on Ames and selected permeability/lipophilicity predictions; the primary finalized profile is retained, without choosing the favorable duplicate. ADMET flags are model predictions, and complete ASKCOS routes are not experimental validation. No ADMET score, continuous route-count score, new composite score or hypothesis test was created.

**Preserved MD inference:** A7 fixed-pocket contacts versus AC-5216 is the only analog-vs-reference primary comparison surviving Holm correction (existing adjusted p=0.031746; four analog comparisons per endpoint). All other MD comparisons above describe means only; non-significant comparisons establish neither superiority nor equivalence. No underlying analysis was rerun or altered.

## Sources and identity handling

The supplementary pharmacokinetics table supplies Final_Weighted_Score unchanged; sensitivity baseline output supplies existing ranks only. This existing score already includes its original component definitions, including docking; it is neither decomposed nor reweighted here. The requested finalized n=5 MD CSV takes precedence over the directory README's older three-replicate description.

Current candidates are mapped by finalized ADMET InChIKey through the existing compound identity map to PBPK enumeration labels:

- A3: `emap2_Bn_CH2CF3`.
- A7: `emap2_Bn-3,4diF_CHF2`.
- A8: `emap2_Bn-3,4diCl_Me`.
- A15: `emap3_Bn-3CF3_4F_Me`.
- AC-5216: `AC5216_ref`.

Current A15 is the F/CF3 candidate formerly A17; legacy A15 is an A8 duplicate and is not used for current A15. A8 uses its retained primary `emap2` PBPK record, not the duplicate `emap3` record. ASKCOS classification text is copied from the master summary; candidate-specific summaries supply corroborating chemistry context.

Source files (all read-only):

- [processed_data_supplements/Supplementary Table - Pharmacokinetics.csv](../processed_data_supplements/Supplementary%20Table%20-%20Pharmacokinetics.csv)
- [PKSim/sensitivity_analysis/pbpk_sensitivity_scores_and_ranks.csv](../PKSim/sensitivity_analysis/pbpk_sensitivity_scores_and_ranks.csv)
- [PKSim/sensitivity_analysis/README.md](../PKSim/sensitivity_analysis/README.md)
- [md/results_summary/replicated_v2/md_primary_endpoint_descriptive_statistics.csv](../md/results_summary/replicated_v2/md_primary_endpoint_descriptive_statistics.csv)
- [md/results_summary/replicated_v2/md_primary_endpoint_vs_AC-5216_statistics.csv](../md/results_summary/replicated_v2/md_primary_endpoint_vs_AC-5216_statistics.csv)
- [ADMET/admet_canonical_profile_v2.csv](../ADMET/admet_canonical_profile_v2.csv)
- [ADMET/admet_identity_audit_v2.csv](../ADMET/admet_identity_audit_v2.csv)
- [ADMET/admet_duplicate_audit_v2.csv](../ADMET/admet_duplicate_audit_v2.csv)
- [audit/tspo_compound_identity_map.csv](../audit/tspo_compound_identity_map.csv)
- [synthesis/askcos/askcos_master_summary.csv](../synthesis/askcos/askcos_master_summary.csv)
- [synthesis/askcos/A3/routes_summary.md](../synthesis/askcos/A3/routes_summary.md)
- [synthesis/askcos/A7/routes_summary.md](../synthesis/askcos/A7/routes_summary.md)
- [synthesis/askcos/A8/routes_summary.md](../synthesis/askcos/A8/routes_summary.md)
- [synthesis/askcos/A15/routes_summary.md](../synthesis/askcos/A15/routes_summary.md)
- [synthesis/askcos/AC-5216/routes_summary.md](../synthesis/askcos/AC-5216/routes_summary.md)

Outputs: [candidate matrix](integrated_candidate_matrix.csv), [Pareto table](pareto_front.csv), [tradeoff figure](integrated_tradeoff_plot.png).
