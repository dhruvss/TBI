# Audited ASKCOS synthesis-feasibility master summary

## Scope and audit method

This aggregate uses only existing files under `synthesis/askcos/`; no ASKCOS, forward-prediction, or condition-recommendation endpoint was run. Canonical structures were taken from the saved per-compound requests. Raw MCTS statistics supplied total pathway, chemical-node, and reaction-node counts.

Complete-route status was independently recalculated from each saved pathway graph: leaf UUIDs were derived from directed pathway edges, resolved through `uuid2smiles`, and checked in `node_dict`. A route was counted as complete only when every leaf was a chemical node with `terminal: true` and a positive `purchase_price`. Thus, pathway presence alone was not treated as proof of completion.

ASKCOS model/template scores and plausibility values are reported separately from literature status. They are model outputs and are not evidence that a reaction has experimental precedent. No composite synthesis score was calculated.

## Master comparison

| Compound | Canonical SMILES | Pathways | Complete routes | Buyable terminal leaves reached | Top route: reaction nodes / longest linear sequence | Main strategy | Most uncertain transformation | Literature status | Final classification |
|---|---|---:|---:|---|---|---|---|---|---|
| AC-5216 | `CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` | 200 | 200 | Yes | 4 / 4 | Purinone N-alkylation with tert-butyl haloacetate, phenyl coupling, deprotection, and amide coupling with N-ethylbenzylamine. | Purinone N-alkylation and access to the advanced N-methyl chloro purinone. | The existing partial summary cites Zhang et al. 2007, but the top raw complete routes have not been independently matched step-for-step to that literature route. **Targeted confirmation required.** | **strong scaffold precedent recovered** |
| A3 | `CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21` | 200 | 200 | Yes | 4 / 4 | Purinone formation, phenyl coupling, N-trifluoroethylation, and side-chain attachment. | N-trifluoroethylation of the di-NH purinone. | AC-5216-like scaffold logic is recovered, but the A3-specific N-trifluoroethylation and its regioselectivity remain unvalidated. **Targeted confirmation required.** | **strong scaffold precedent recovered** |
| A7 | `CCN(Cc1cc(F)ccc1F)C(=O)Cn1c(=O)n(C(F)F)c2cnc(-c3ccccc3)nc21` | 0 | 0 | No | No complete route; three selected partial branches contain one transformation each | Side-chain acid chloride/acid/ester disconnections preserving an already N-difluoromethylated core. | Preparation of the N-difluoromethylated purinone core. | Related chemistry is mentioned in the existing summary, but exact scaffold-specific/regioselective precedent is not validated. **Targeted confirmation required.** | **plausible route with one unresolved key step** |
| A8 | `CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` | 200 | 200 | Yes | 3 / 3 | A8-specific alpha-halo amide preparation, purinone N-alkylation, and phenyl coupling. | N-alkylation with the bulky 3,4-dichlorobenzyl-containing alpha-bromo amide. | Strong AC-5216 analogy is documented, but the exact substrate combination and advanced purinone availability lack targeted validation. **Targeted confirmation required.** | **strong scaffold precedent recovered** |
| A15 | `CCN(Cc1cc(F)ccc1C(F)(F)F)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` | 200 | 200 | Yes | 5 / 4 | Parallel benzylamine and purinone-acid preparation, amide coupling, and phenyl coupling. | Selective formation of the F/CF3-substituted secondary benzylamine from ethylamine and the exact benzyl halide. | The route is AC-5216-like, but exact benzyl-halide accessibility and monoalkylation precedent are not validated. **Targeted confirmation required.** | **strong scaffold precedent recovered** |

## ASKCOS score context

| Compound | Score scope | Model/template score range | Plausibility range | Interpretation limit |
|---|---|---:|---:|---|
| AC-5216 | Best complete route, four reactions | 0.0018141075–0.1526162326 | 0.9995749593–0.9999071360 | Complete/buyable in the raw ASKCOS graph; not a step-for-step literature validation. |
| A3 | Best complete route, four reactions | 0.00005704645–0.0311400555 | 0.9985127449–0.9999836683 | The very low N-trifluoroethylation model score and regioselectivity still require manual review despite high plausibility. |
| A7 | Three selected partial branches | 0.0019880994–0.1700970680 | 0.9996905327–0.9999837875 | These values support side-chain disconnections only; they do not support direct N-difluoromethylation. |
| A8 | Best complete route, three reactions | 0.0009487294–0.7300161123 | 0.9994654655–1.0000000000 | High predicted plausibility does not validate the exact bulky N-alkylation experimentally. |
| A15 | Best complete route, five reactions | 0.0179738421–0.4464313686 | 0.9987807870–0.9999974370 | Scores do not establish availability of the exact F/CF3-substituted benzyl halide or selective monoalkylation. |

Pathway-level scores are unavailable (`null`) for the complete-route outputs, so no pathway score is inferred or substituted.

## Compound-specific audit conclusions

### AC-5216

The raw response contains 200 pathways and 200 complete routes; all 910 pathway leaves are terminal and buyable under the returned metadata. The best raw route has four reaction nodes and a longest linear sequence of four: purinone N-alkylation with tert-butyl bromoacetate, phenyl installation from a boronate, tert-butyl ester deprotection, and amide coupling with N-ethylbenzylamine.

The AC-5216 derived route summaries were corrected after an audit found that their earlier route-count statement contradicted `raw_mcts_response.json`. The raw graph, corrected AC-5216 summaries, and this master summary now agree on 200 complete buyable-terminal routes.

The existing partial summary cites a Zhang et al. 2007 benchmark and identifies desmethyl/late-methylation and side-chain-disconnection motifs. That citation supports a broad scaffold precedent claim, but the best raw complete route has not been independently checked against the cited paper in this aggregation.

### A3

All 200 pathways are complete and buyable-terminal. The four-step best route explicitly forms the purinone, installs phenyl, installs N-CH2CF3, and adds the benzyl-ethylamide side chain. The N-trifluoroethyl group is genuinely introduced when the di-NH purinone reacts with 2,2,2-trifluoroethyl chloride; this is the main chemistry needing targeted literature review for reactivity and N-regioselectivity.

### A7

The raw response contains zero pathways and therefore zero complete routes. ASKCOS recovered three chemically coherent one-reaction partial branches involving side-chain disconnection while preserving an already N-difluoromethylated purinone core.

The A7 audit remains decisive: 591 reaction nodes contain CHF2, but this is a presence count rather than an installation count, and genuine CHF2-installation reactions equal zero. Seven apparent text-based installations are equivalent SMILES representations (`FC(F)n1...` versus `...n1C(F)F`), not chemical installation events. Exact preparation and regioselectivity of the N-difluoromethylated purinone core require targeted literature confirmation.

### A8

All 200 pathways are complete and buyable-terminal. The three-step best route prepares the 3,4-dichlorobenzyl-containing alpha-bromo amide, alkylates the remaining N-H of an already N-methylated chloro purinone, and installs phenyl by boronate coupling. The dichlorobenzyl group is pre-existing in the side-chain reagent; the key review point is practical chemoselectivity of the bulky N-alkylation and access to the advanced purinone precursor.

### A15

All 200 pathways are complete and buyable-terminal. The best convergent pathway has five reaction nodes and longest linear depth four: it prepares the F/CF3-substituted N-ethylbenzylamine and purinone acetic acid in parallel, couples them, and installs phenyl on the heterocycle.

The aryl F and CF3 groups are already present in the benzyl bromide and are preserved through benzylamine formation and amide coupling. The A15-specific literature question is therefore not installation of those groups, but availability of the exact substituted benzyl halide and control of ethylamine monoalkylation versus overalkylation.

## Targeted literature-confirmation register

- **AC-5216:** Match the raw top complete route to the cited Zhang et al. 2007 synthesis or another primary source; verify the advanced N-methyl chloro purinone and haloacetate N-alkylation.
- **A3:** Validate N-trifluoroethylation reagent performance and N-regioselectivity on the proposed purinone; confirm the purinone-forming step.
- **A7:** Identify exact scaffold-specific precedent for regioselective N-difluoromethylation or an alternative preparation of the N-difluoromethylated core.
- **A8:** Confirm the convergent purinone N-alkylation with the 3,4-dichlorobenzyl alpha-bromo amide and practical availability of the advanced chloro purinone.
- **A15:** Confirm availability or preparation of the exact F/CF3-substituted benzyl halide and conditions favoring secondary benzylamine formation without overalkylation.

These flags identify evidence gaps only; they do not replace ASKCOS outputs with literature claims and do not constitute condition recommendations.
