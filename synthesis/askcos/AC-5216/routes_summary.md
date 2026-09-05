# ASKCOS-predicted retrosynthetic routes for AC-5216

This corrected summary uses the saved result from the public ASKCOS MCTS endpoint for:

`CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21`

No new ASKCOS search was run.

## Audited route status

- ASKCOS execution status: successful
- Total pathways returned: 200
- Complete terminal routes: 200
- Buyable-terminal routes: 200
- Chemical nodes: 2,244
- Reaction nodes: 3,344
- Pathway-level scores: unavailable (`null`)

Completeness was verified from the raw pathway graphs. For each pathway, leaf UUIDs were derived from directed edges and resolved through `uuid2smiles` into `node_dict`. All 910 leaves across the 200 pathways are chemical nodes with `terminal: true` and positive `purchase_price`; all 200 pathways are therefore complete and buyable-terminal under the returned metadata.

## Top complete routes

### Route 1 — index 1

**Reaction nodes / longest linear sequence:** 4 / 4
**Terminal materials:** tert-butyl bromoacetate, phenylboronic acid pinacol ester, N-ethylbenzylamine, and `Cn1c(=O)[nH]c2nc(Cl)ncc21`; all are marked terminal and buyable.

Product → precursor sequence:

1. AC-5216 → N-ethylbenzylamine + N-methyl phenyl-purinone acetic acid.
2. Purinone acetic acid → its tert-butyl ester.
3. Phenyl-purinone ester → phenylboronic acid pinacol ester + chloro-purinone ester.
4. Chloro-purinone ester → tert-butyl bromoacetate + N-methyl chloro purinone.

Reaction SMILES and model outputs:

1. `CCNCc1ccccc1.Cn1c(=O)n(CC(=O)O)c2nc(-c3ccccc3)ncc21>>CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21` — model score 0.1526162326; plausibility 0.9998746514.
2. `Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(-c3ccccc3)ncc21>>Cn1c(=O)n(CC(=O)O)c2nc(-c3ccccc3)ncc21` — model score 0.1432971954; plausibility 0.9995749593.
3. `CC1(C)OB(c2ccccc2)OC1(C)C.Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(Cl)ncc21>>Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(-c3ccccc3)ncc21` — model score 0.0018141075; plausibility 0.9999071360.
4. `CC(C)(C)OC(=O)CBr.Cn1c(=O)[nH]c2nc(Cl)ncc21>>Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(Cl)ncc21` — model score 0.0179739296; plausibility 0.9998890162.

This is a coherent convergent strategy: purinone N-alkylation with a haloacetate, heteroaryl phenyl coupling, ester deprotection, and amide coupling with N-ethylbenzylamine.

### Route 2 — index 2

**Reaction nodes / longest linear sequence:** 4 / 4
**Terminal materials:** tert-butyl chloroacetate, phenylboronic acid pinacol ester, N-ethylbenzylamine, and `Cn1c(=O)[nH]c2nc(Cl)ncc21`; all are marked terminal and buyable.

Route 2 is identical to route 1 except that purinone N-alkylation uses tert-butyl chloroacetate:

`CC(C)(C)OC(=O)CCl.Cn1c(=O)[nH]c2nc(Cl)ncc21>>Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(Cl)ncc21`

The model score is 0.0099217165 and plausibility is 0.9998646975. The remaining three reaction records and values are identical to route 1.

### Route 3 — index 3

**Reaction nodes / longest linear sequence:** 4 / 4
**Terminal materials:** tert-butyl bromoacetate, phenylboronic acid pinacol ester, N-ethylbenzylamine, and `Cn1c(=O)[nH]c2nc(Cl)ncc21`; all are marked terminal and buyable.

Route 3 changes the order of phenyl installation and haloacetate N-alkylation. Its distinguishing transformations are:

- `CC(C)(C)OC(=O)CBr.Cn1c(=O)[nH]c2nc(-c3ccccc3)ncc21>>Cn1c(=O)n(CC(=O)OC(C)(C)C)c2nc(-c3ccccc3)ncc21` — model score 0.0769360662; plausibility 0.9999899864.
- `CC1(C)OB(c2ccccc2)OC1(C)C.Cn1c(=O)[nH]c2nc(Cl)ncc21>>Cn1c(=O)[nH]c2nc(-c3ccccc3)ncc21` — model score 0.00009003081; plausibility 0.9996894598.

The ester-deprotection and final amide-coupling reactions match route 1.

## Supplementary partial-branch chemistry

The complete-route audit does not invalidate other useful reaction nodes in the tree. The separately saved partial-branch analysis identifies a desmethyl precursor/late N-methylation motif, the N-benzyl-N-ethyl acetamide side-chain disconnection, and an ester/acid interconversion involving the purinone acetic-acid precursor.

These motifs remain useful for comparison with the cited Zhang et al. 2007 strategy, but they are supplementary observations and must not be confused with the verified count of 200 complete routes.

## Interpretation

The raw ASKCOS graph recovers strong scaffold precedent and complete buyable-terminal pathways. This is not a declaration that every transformation has been experimentally validated or that the top pathway exactly reproduces the cited literature synthesis. Model/template scores and plausibilities are predictions; the advanced N-methyl chloro purinone and its haloacetate N-alkylation remain appropriate targets for focused literature confirmation.
