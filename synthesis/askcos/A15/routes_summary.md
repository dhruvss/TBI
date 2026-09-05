# A15 ASKCOS synthesis-feasibility analysis

## Structure validation

- Authoritative current source: `ADMET/admet_canonical_profile_v2.csv`, A15 `Primary canonical record`
- Identity confirmation: `ADMET/admet_identity_audit_v2.csv`, A15 status `Passed`
- Exact SMILES: `CCN(Cc1cc(F)ccc1C(F)(F)F)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21`
- RDKit parse result: successful
- RDKit canonical SMILES: `CCN(Cc1cc(F)ccc1C(F)(F)F)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21`

The retired legacy A15 identifier that duplicated A8 was not used. The current A15 record is the fluorinated/trifluoromethyl benzyl analog with InChIKey `BMDVLVHNGCQESR-UHFFFAOYSA-N`.

## API completion and route status

- Endpoint: `https://askcos.mit.edu/api/tree-search/mcts/call-sync-without-token`
- Requests: one conservative synchronous MCTS call using the established default live request style
- Result: status 200; `mcts.call_raw() successfully executed.`
- Total pathways: 200
- Complete buyable-terminal routes: 200
- Chemical nodes: 622
- Reaction nodes: 904
- Pathway scores: unavailable (`score: null`)
- Forward prediction and condition recommendation: not run

Completeness was verified for each pathway by deriving leaf UUIDs from its directed edges, resolving them through `uuid2smiles`, and checking the corresponding `node_dict` records. Every leaf in all 200 pathways is a chemical node with `terminal: true` and a positive `purchase_price`.

## Top three complete routes

Each selected pathway contains five reaction nodes arranged in a convergent route with longest linear depth four.

### Route 1 — index 1

**Terminal starting materials:** tert-butyl bromoacetate (buyable, 1.0), phenylboronic acid pinacol ester (buyable, 0.43), ethylamine (buyable, 13.0), `Cn1c(=O)[nH]c2nc(Cl)ncc21` (buyable, 1813.5), and `Fc1ccc(C(F)(F)F)c(CBr)c1` (buyable, 4.0).

Product → precursor sequence:

1. A15 → phenylboronic acid pinacol ester + chloro-core A15 intermediate.
2. Chloro-core A15 intermediate → substituted N-ethylbenzylamine + N-methyl purinone acetic acid.
3. Purinone acetic acid → its tert-butyl ester.
4. Purinone tert-butyl ester → tert-butyl bromoacetate + N-methyl chloro purinone.
5. Substituted N-ethylbenzylamine → ethylamine + fluorinated/trifluoromethyl benzyl bromide.

| Step | Reaction SMILES | Model/template score | Plausibility | Class |
|---:|---|---:|---:|---|
| 1 | `CC1(C)OB(c2ccccc2)OC1(C)C.CCN(Cc1cc(F)ccc1C(F)(F)F)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21>>CCN(Cc1cc(F)ccc1C(F)(F)F)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` | 0.4464313686 | 0.9999974370 | Heteroaryl C–Cl replacement by phenyl boronate coupling. |
| 2 | `CCNCc1cc(F)ccc1C(F)(F)F.Cn1c(=O)n(CC(=O)O)c2nc(Cl)ncc21>>CCN(Cc1cc(F)ccc1C(F)(F)F)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21` | 0.0535887070 | 0.9999861717 | Amide coupling of substituted secondary benzylamine and purinone acetic acid. |
| 3 | `Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(Cl)ncc21>>Cn1c(=O)n(CC(=O)O)c2nc(Cl)ncc21` | 0.1363359988 | 0.9992824793 | tert-Butyl ester deprotection. |
| 4 | `CC(C)(C)OC(=O)CBr.Cn1c(=O)[nH]c2nc(Cl)ncc21>>Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(Cl)ncc21` | 0.0179738421 | 0.9998890162 | Purinone N-alkylation with tert-butyl bromoacetate. |
| 5 | `CCN.Fc1ccc(C(F)(F)F)c(CBr)c1>>CCNCc1cc(F)ccc1C(F)(F)F` | 0.0528475195 | 0.9987807870 | Benzyl-bromide substitution by ethylamine. |

### Route 2 — index 2

**Terminal starting materials:** tert-butyl chloroacetate (buyable, 1.0), phenylboronic acid pinacol ester (buyable, 0.43), ethylamine (buyable, 13.0), `Cn1c(=O)[nH]c2nc(Cl)ncc21` (buyable, 1813.5), and `Fc1ccc(C(F)(F)F)c(CBr)c1` (buyable, 4.0).

This route has the same product → precursor sequence as route 1, but step 4 uses tert-butyl chloroacetate:

`CC(C)(C)OC(=O)CCl.Cn1c(=O)[nH]c2nc(Cl)ncc21>>Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(Cl)ncc21`

- Step 4 model/template score: 0.0099216886
- Step 4 plausibility: 0.9998646975
- Other reaction SMILES, scores, plausibilities, and classes are identical to route 1.

### Route 3 — index 3

**Terminal starting materials:** tert-butyl bromoacetate (buyable, 1.0), phenylboronic acid pinacol ester (buyable, 0.43), ethylamine (buyable, 13.0), `Cn1c(=O)[nH]c2nc(Cl)ncc21` (buyable, 1813.5), and `Fc1ccc(C(F)(F)F)c(CCl)c1` (buyable, 1.0).

This route matches route 1 except that the substituted benzylamine is prepared from the corresponding benzyl chloride:

`CCN.Fc1ccc(C(F)(F)F)c(CCl)c1>>CCNCc1cc(F)ccc1C(F)(F)F`

- Benzyl substitution model/template score: 0.0054391790
- Benzyl substitution plausibility: 0.9983855486
- Other reaction SMILES, scores, plausibilities, and classes are identical to route 1.

Full route-step records and reaction-class assignments are preserved in `routes_summary.csv`; the exact returned template SMARTS remain available in `raw_mcts_response.json`.

## Scaffold comparison and connectivity audit

Standard AC-5216-like transformations are purinone N-alkylation with a haloacetate, ester deprotection, amide coupling to an N-ethylbenzylamine, and heteroaryl phenyl installation by boronate coupling. The N-methyl group is already present in `Cn1c(=O)[nH]c2nc(Cl)ncc21` and is preserved throughout; it is not installed by any selected reaction.

The A15-specific branch is formation of `CCNCc1cc(F)ccc1C(F)(F)F` by substitution of the corresponding fluorinated/trifluoromethyl benzyl bromide or chloride with ethylamine. RDKit connectivity inspection confirms that the benzyl C–halogen bond is replaced by a benzyl C–N bond. The aryl F and CF₃ groups are already present in the benzyl-halide reactant and remain unchanged, so no selected step installs either substituent.

The unusual A15 substituent pattern therefore does not introduce a new reaction class. Its principal extra concern is access to the specifically substituted benzyl halide and control of monoalkylation versus overalkylation with ethylamine; ASKCOS marks both benzyl-halide variants terminal and buyable.

## Most uncertain transformation in the best route

The most uncertain transformation is formation of the A15-specific secondary benzylamine from ethylamine and `Fc1ccc(C(F)(F)F)c(CBr)c1`. This is a conventional benzyl substitution, but it uniquely introduces the A15 side-chain building block and may require control of overalkylation; practical accessibility of the exact fluorinated/trifluoromethyl benzyl bromide should also be confirmed. Connectivity inspection verifies that the new bond is benzyl C–N and that F and CF₃ are pre-existing substituents, avoiding the A7-type misclassification.

## Final synthesis-feasibility classification

**strong scaffold precedent recovered**

ASKCOS returned complete buyable-terminal routes dominated by standard AC-5216-like purinone N-alkylation, ester handling, amide formation, and heteroaryl coupling. The A15-specific fluorinated/trifluoromethyl benzylamine branch uses conventional substitution chemistry and does not create a fundamentally new synthetic challenge, although exact benzyl-halide accessibility and monoalkylation selectivity merit manual confirmation.
