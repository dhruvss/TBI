# A3 ASKCOS synthesis-feasibility analysis

## A3 structure validation

- Authoritative source: `audit/tspo_unique_compounds.csv`, primary record `TSPO-C03` / current ID `A3`
- Exact repository SMILES: `CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21`
- RDKit parse result: successful (`MolFromSmiles` returned a molecule)
- RDKit canonical SMILES: `CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21`

No legacy identifier or external structure was used.

## API completion status

- Endpoint: `https://askcos.mit.edu/api/tree-search/mcts/call-sync-without-token`
- Workflow: one conservative synchronous public MCTS request using the same default live request style used for AC-5216 and A7
- Status: HTTP/API status 200; `mcts.call_raw() successfully executed.`
- Search statistics: 32 iterations, 628 chemical nodes, 829 reaction nodes, and 200 returned pathways
- Complete terminal routes: 200
- Forward prediction and condition recommendation: not run

All leaves in the 200 returned pathways resolve to chemical nodes marked `terminal: true`. The following are the top three complete pathways in the API-returned order.

## Route 1 — API rank 1 (best route)

**Status:** Complete; four represented reaction steps; all five terminal precursors are marked buyable.

### Product → precursor sequence

1. A3 → `CCN(Cc1ccccc1)C(=O)CCl` + `O=c1[nH]c2nc(-c3ccccc3)ncc2n1CC(F)(F)F`
2. N-trifluoroethyl phenyl purinone → `FC(F)(F)CCl` + `O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1`
3. Phenyl purinone → `O=c1[nH]c2cnc(Cl)nc2[nH]1` + `OB(O)c1ccccc1`
4. Chloro purinone → `NC(N)=O` + `Nc1cnc(Cl)nc1N`

### Reaction data

| Step | Reaction SMILES | Model/template score | Plausibility | Assessment |
|---:|---|---:|---:|---|
| 1 | `CCN(Cc1ccccc1)C(=O)CCl.O=c1[nH]c2nc(-c3ccccc3)ncc2n1CC(F)(F)F>>CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21` | 0.0030236701 | 0.9999836683 | Straightforward heterocycle N-alkylation with the preassembled benzyl-ethylamide side chain. |
| 2 | `FC(F)(F)CCl.O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1>>O=c1[nH]c2nc(-c3ccccc3)ncc2n1CC(F)(F)F` | 0.00005704645 | 0.9986171722 | Plausible N-trifluoroethyl installation, but low model support and possible N-regioselectivity require manual review. |
| 3 | `O=c1[nH]c2cnc(Cl)nc2[nH]1.OB(O)c1ccccc1>>O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1` | 0.0311400555 | 0.9985127449 | Literature-like aryl installation from a chloro heterocycle and phenylboronic acid. |
| 4 | `NC(N)=O.Nc1cnc(Cl)nc1N>>O=c1[nH]c2cnc(Cl)nc2[nH]1` | 0.0035977473 | 0.9996422529 | Plausible purinone ring formation; literature-like but conditions still require later validation. |

**Terminal materials:** `CCN(Cc1ccccc1)C(=O)CCl`, `FC(F)(F)CCl`, `NC(N)=O`, `Nc1cnc(Cl)nc1N`, and `OB(O)c1ccccc1`; each has `terminal: true` and a positive purchase price in the response.

**Relationship to AC-5216:** Strongly resembles the AC-5216 scaffold strategy: construct the purinone, install the phenyl group, functionalize the ring nitrogen, and attach the same benzyl-ethylamide-bearing chloromethyl ketone side chain. A3 replaces AC-5216's N-methyl substituent with N-CH₂CF₃.

## Route 2 — API rank 2

**Status:** Complete; five represented reaction steps; all six terminal precursors are marked buyable.

### Product → precursor sequence

1. A3 → ethyl tosylate + secondary benzylamide A3 precursor
2. Secondary benzylamide precursor → `O=C(CBr)NCc1ccccc1` + N-trifluoroethyl phenyl purinone
3. N-trifluoroethyl phenyl purinone → `FC(F)(F)CCl` + phenyl purinone
4. Phenyl purinone → chloro purinone + phenylboronic acid
5. Chloro purinone → urea + `Nc1cnc(Cl)nc1N`

### Reaction data

| Step | Reaction SMILES | Model/template score | Plausibility | Assessment |
|---:|---|---:|---:|---|
| 1 | `CCOS(=O)(=O)c1ccc(C)cc1.O=C(Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21)NCc1ccccc1>>CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21` | 0.00066617754 | 0.9996609688 | Late N-ethylation of a secondary amide; requires manual review and is less attractive than route 1. |
| 2 | `O=C(CBr)NCc1ccccc1.O=c1[nH]c2nc(-c3ccccc3)ncc2n1CC(F)(F)F>>O=C(Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21)NCc1ccccc1` | 0.0070227082 | 0.9999964237 | Straightforward heterocycle N-alkylation in concept. |
| 3 | `FC(F)(F)CCl.O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1>>O=c1[nH]c2nc(-c3ccccc3)ncc2n1CC(F)(F)F` | 0.00005704645 | 0.9986171722 | N-trifluoroethylation requires manual regioselectivity review. |
| 4 | `O=c1[nH]c2cnc(Cl)nc2[nH]1.OB(O)c1ccccc1>>O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1` | 0.0311400555 | 0.9985127449 | Literature-like aryl coupling. |
| 5 | `NC(N)=O.Nc1cnc(Cl)nc1N>>O=c1[nH]c2cnc(Cl)nc2[nH]1` | 0.0035977473 | 0.9996422529 | Plausible purinone ring formation. |

**Terminal materials:** ethyl tosylate, `O=C(CBr)NCc1ccccc1`, `FC(F)(F)CCl`, urea, `Nc1cnc(Cl)nc1N`, and phenylboronic acid; all are marked `terminal: true` with positive purchase prices.

## Route 3 — API rank 3

**Status:** Complete; four represented reaction steps; all five terminal precursors are marked buyable.

This route is identical to route 1 for side-chain installation, N-trifluoroethylation, and phenyl coupling. It differs only in purinone formation, using a CDI-type carbonyl source.

### Product → precursor sequence

1. A3 → `CCN(Cc1ccccc1)C(=O)CCl` + N-trifluoroethyl phenyl purinone
2. N-trifluoroethyl phenyl purinone → `FC(F)(F)CCl` + phenyl purinone
3. Phenyl purinone → chloro purinone + phenylboronic acid
4. Chloro purinone → `Nc1cnc(Cl)nc1N` + `O=C(n1ccnc1)n1ccnc1`

### Reaction data

| Step | Reaction SMILES | Model/template score | Plausibility | Assessment |
|---:|---|---:|---:|---|
| 1 | `CCN(Cc1ccccc1)C(=O)CCl.O=c1[nH]c2nc(-c3ccccc3)ncc2n1CC(F)(F)F>>CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(CC(F)(F)F)c2cnc(-c3ccccc3)nc21` | 0.0030236701 | 0.9999836683 | Straightforward side-chain N-alkylation. |
| 2 | `FC(F)(F)CCl.O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1>>O=c1[nH]c2nc(-c3ccccc3)ncc2n1CC(F)(F)F` | 0.00005704645 | 0.9986171722 | Requires manual review for N-regioselectivity. |
| 3 | `O=c1[nH]c2cnc(Cl)nc2[nH]1.OB(O)c1ccccc1>>O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1` | 0.0311400555 | 0.9985127449 | Literature-like aryl coupling. |
| 4 | `Nc1cnc(Cl)nc1N.O=C(n1ccnc1)n1ccnc1>>O=c1[nH]c2cnc(Cl)nc2[nH]1` | 0.00037395005 | 0.9992832541 | Plausible CDI-mediated purinone formation, but lower model support than route 1's urea variant. |

**Terminal materials:** `CCN(Cc1ccccc1)C(=O)CCl`, `FC(F)(F)CCl`, `Nc1cnc(Cl)nc1N`, `O=C(n1ccnc1)n1ccnc1`, and phenylboronic acid; all are marked `terminal: true` with positive purchase prices.

## Most uncertain transformation in the best route

The most uncertain transformation is N-trifluoroethylation of `O=c1[nH]c2cnc(-c3ccccc3)nc2[nH]1` with 2,2,2-trifluoroethyl chloride (`FC(F)(F)CCl`). Although ASKCOS assigns high plausibility (0.998617), its template/model score is only 0.00005704645 (rank 17). The substrate has two N-H sites, so the required N-regioselectivity and practical reactivity of the chloride electrophile need manual literature or experimental validation. The N-CH₂CF₃ group is installed at this step and preserved during the final side-chain alkylation.

## Final synthesis-feasibility classification

**Strong scaffold precedent recovered.**

ASKCOS returned complete, buyable-terminal routes that closely follow the known AC-5216 scaffold logic. Purinone construction, phenyl installation, and benzyl-ethylamide side-chain attachment are coherently represented. The principal A3-specific uncertainty is regioselective N-trifluoroethyl installation; this warrants manual review but does not erase the strong recovered scaffold precedent.
