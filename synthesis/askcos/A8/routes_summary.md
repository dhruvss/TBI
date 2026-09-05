# A8 ASKCOS synthesis-feasibility analysis

## Structure validation

- Authoritative source: `audit/tspo_unique_compounds.csv`, retained primary record `TSPO-C08` / current ID `A8`
- Exact SMILES: `CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21`
- RDKit parse: successful
- RDKit canonical SMILES: `CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21`

The technical duplicate `A8_2`, retired legacy alias `A15`, and external structures were not used.

## API and route completeness

- Endpoint: `https://askcos.mit.edu/api/tree-search/mcts/call-sync-without-token`
- Calls made: one conservative synchronous MCTS call with the established default live request style
- API result: status 200; `mcts.call_raw() successfully executed.`
- Search statistics: 33 iterations, 570 chemical nodes, 737 reaction nodes, 200 pathways
- Complete terminal routes: 200
- Pathway scores: unavailable (`score: null` in pathway metadata)
- Forward prediction and condition recommendation: not run

Completeness was not inferred from pathway presence. For every pathway, leaf UUIDs were derived from its directed edges and resolved through `uuid2smiles` into `node_dict`. All leaves in all 200 pathways are chemical nodes with `terminal: true` and positive `purchase_price` values; therefore all 200 qualify as complete buyable-terminal routes under the returned metadata.

## Top three complete routes

### Route 1 — index 1

**Represented steps:** 3  
**Pathway score:** unavailable  
**Terminal materials:** phenylboronic acid pinacol ester (buyable, 0.43), `CCNCc1cc(Cl)ccc1Cl` (buyable, 1.0), `Cn1c(=O)[nH]c2nc(Cl)ncc21` (buyable, 1813.5), and dibromoacetyl bromide (buyable, 1.0).

Product → precursor sequence:

1. A8 → phenylboronic acid pinacol ester + chloro-core A8 intermediate.
2. Chloro-core A8 intermediate → A8-specific alpha-bromo tertiary amide + N-methyl chloro purinone.
3. A8-specific alpha-bromo tertiary amide → N-ethyl-3,4-dichlorobenzylamine + dibromoacetyl bromide.

| Step | Reaction SMILES | Model/template score | Plausibility | Class and assessment |
|---:|---|---:|---:|---|
| 1 | `CC1(C)OB(c2ccccc2)OC1(C)C.CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` | 0.0734166130 | 1.0 | Heteroaryl C–Cl replacement by phenyl boronate coupling; literature-like scaffold arylation. |
| 2 | `CCN(Cc1cc(Cl)ccc1Cl)C(=O)CBr.Cn1c(=O)[nH]c2nc(Cl)ncc21>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21` | 0.0009487294 | 0.9994654655 | Purinone N-alkylation with an alpha-bromo tertiary amide; convergent and analogous to AC-5216, but merits manual review. |
| 3 | `CCNCc1cc(Cl)ccc1Cl.O=C(Br)CBr>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)CBr` | 0.7300161123 | 0.9996379614 | Amide formation from a secondary amine and bromoacetyl bromide; straightforward side-chain electrophile preparation. |

### Route 2 — index 2

**Represented steps:** 3  
**Pathway score:** unavailable  
**Terminal materials:** `CCNCc1cc(Cl)ccc1Cl` (buyable, 1.0), `Cn1c(=O)[nH]c2nc(Cl)ncc21` (buyable, 1813.5), dibromoacetyl bromide (buyable, 1.0), and phenylboronic acid (buyable, 0.39).

Product → precursor sequence:

1. A8 → phenylboronic acid + chloro-core A8 intermediate.
2. Chloro-core A8 intermediate → A8-specific alpha-bromo tertiary amide + N-methyl chloro purinone.
3. A8-specific alpha-bromo tertiary amide → N-ethyl-3,4-dichlorobenzylamine + dibromoacetyl bromide.

| Step | Reaction SMILES | Model/template score | Plausibility | Class and assessment |
|---:|---|---:|---:|---|
| 1 | `CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21.OB(O)c1ccccc1>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` | 0.0176180378 | 0.9999519587 | Phenylboronic-acid variant of the same literature-like heteroaryl coupling. |
| 2 | `CCN(Cc1cc(Cl)ccc1Cl)C(=O)CBr.Cn1c(=O)[nH]c2nc(Cl)ncc21>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21` | 0.0009487294 | 0.9994654655 | Same convergent purinone N-alkylation as route 1. |
| 3 | `CCNCc1cc(Cl)ccc1Cl.O=C(Br)CBr>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)CBr` | 0.7300161123 | 0.9996379614 | Same straightforward side-chain electrophile preparation as route 1. |

### Route 3 — index 3

**Represented steps:** 3  
**Pathway score:** unavailable  
**Terminal materials:** phenylboronic acid pinacol ester (buyable, 0.43), `CCNCc1cc(Cl)ccc1Cl` (buyable, 1.0), `Cn1c(=O)[nH]c2nc(Cl)ncc21` (buyable, 1813.5), and bromoacetyl chloride (buyable, 1.0).

Product → precursor sequence:

1. A8 → phenylboronic acid pinacol ester + chloro-core A8 intermediate.
2. Chloro-core A8 intermediate → A8-specific alpha-bromo tertiary amide + N-methyl chloro purinone.
3. A8-specific alpha-bromo tertiary amide → N-ethyl-3,4-dichlorobenzylamine + bromoacetyl chloride.

| Step | Reaction SMILES | Model/template score | Plausibility | Class and assessment |
|---:|---|---:|---:|---|
| 1 | `CC1(C)OB(c2ccccc2)OC1(C)C.CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` | 0.0734166130 | 1.0 | Same literature-like heteroaryl coupling as route 1. |
| 2 | `CCN(Cc1cc(Cl)ccc1Cl)C(=O)CBr.Cn1c(=O)[nH]c2nc(Cl)ncc21>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)Cn1c(=O)n(C)c2cnc(Cl)nc21` | 0.0009487294 | 0.9994654655 | Same convergent purinone N-alkylation as routes 1 and 2. |
| 3 | `CCNCc1cc(Cl)ccc1Cl.O=C(Cl)CBr>>CCN(Cc1cc(Cl)ccc1Cl)C(=O)CBr` | 0.0402525999 | 0.9995697141 | Acid-chloride variant of side-chain electrophile preparation. |

## Structural transformation audit

The assignments above were checked by parsing all reaction components with RDKit and comparing molecular connectivity, not by substring matching:

- Aryl coupling: the heterocyclic precursor has a core C–Cl bond at the position where the product has a core C–phenyl bond; the phenyl group comes from the boronic acid/ester reagent.
- Convergent N-alkylation: the purinone reactant has one explicit `[nH]`, while its other ring nitrogen already bears methyl (`Cn1...`). The product replaces that N–H with an N–CH₂ bond to the alpha-carbon of the bromoamide. The N-methyl substituent is preserved, not installed in this step.
- Side-chain formation: N-ethyl-3,4-dichlorobenzylamine becomes the tertiary amide on reaction with bromoacetyl bromide or bromoacetyl chloride. Both aryl chlorines remain on the benzyl ring; they are not introduced later.

Thus, the genuinely A8-specific element is the 3,4-dichlorobenzyl-containing amine/electrophile. The N-methyl purinone, phenyl installation, and convergent benzyl/ethylamide side-chain attachment follow the established AC-5216 scaffold logic. The top routes stop at an advanced N-methyl chloro purinone marked buyable by ASKCOS and do not independently demonstrate formation of that purinone core.

## Most uncertain transformation in the best route

The step most deserving manual literature review is alkylation of `Cn1c(=O)[nH]c2nc(Cl)ncc21` with `CCN(Cc1cc(Cl)ccc1Cl)C(=O)CBr`. Structural comparison confirms that this step actually forms the purinone N–CH₂(side-chain) bond and that the N-methyl group is already present. The remaining `[nH]` limits the regioisomer question, and the reaction is strongly analogous to the AC-5216 strategy; review should focus on practical chemoselectivity and reactivity of the bulky alpha-bromo tertiary amide rather than on a suspected novel transformation.

## Final synthesis-feasibility classification

**strong scaffold precedent recovered**

All top routes are complete under the returned terminal/buyability metadata and use recognizable AC-5216 chemistry: convergent purinone N-alkylation, heteroaryl phenyl coupling, and benzyl/ethylamide side-chain construction. A8-specific chemistry is largely confined to carrying the 3,4-dichlorobenzyl substituent through a conventional amide precursor, while the advanced purinone starting material and key N-alkylation remain appropriate targets for manual availability and literature confirmation.
