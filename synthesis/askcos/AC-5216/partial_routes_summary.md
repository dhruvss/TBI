# Partial ASKCOS-predicted retrosynthetic branches for AC-5216

This summary uses the saved ASKCOS MCTS result in `raw_mcts_response.json` and does not run a new MCTS search. The goal is to identify nonterminal branches that still express chemically interpretable retrosynthetic motifs consistent with the known AC-5216 scaffold strategy.

## Benchmark context

The benchmark strategy uses the Zhang et al. 2007 synthesis as the external reference for AC-5216. In that literature route, a desmethyl precursor of AC-5216 is formed and then methylated late to give the final N-methyl imide. The ASKCOS tree contains several nonterminal branches that support this general logic even though none are marked as terminal complete routes.

## Branch 1: desmethyl precursor / late methylation motif

Target product:
CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21

Branch transformation:
CCN(Cc1ccccc1)C(=O)Cn1c(=O)[nH]c2cnc(-c3ccccc3)nc21.CI>>CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21

Interpretation:
- This is the clearest match to the known literature strategy.
- The precursor is the desmethyl N-H analogue; the product is the final N-methyl AC-5216.
- The reaction template is a methylation template from the ASKCOS reaxys backend.
- Reported model score: 0.19088222086429596
- Reported plausibility: 0.9992062449455261

Assessment:
- Chemically interpretable: yes
- Consistent with known AC-5216 scaffold strategy: yes

## Branch 2: N-benzyl-N-ethyl acetamide side-chain disconnection

Target product:
CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21

Branch transformation:
CCNCc1ccccc1.Cn1c(=O)n(CC(=O)O)c2nc(-c3ccccc3)ncc21>>CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21

Interpretation:
- The ASKCOS tree breaks the target into an N-benzyl-ethylamine fragment and a carboxylate-containing purinone precursor.
- This is a chemically coherent disconnection of the N-benzyl-N-ethyl acetamide side chain.
- Template SMARTS encode amide cleavage / acyl transfer logic.
- Reported model score: 0.1526162326335907
- Reported plausibility: 0.9998746514320374

Assessment:
- Chemically interpretable: yes
- Consistent with known AC-5216 scaffold strategy: yes

## Branch 3: purinone / purine core opening to a carboxylate precursor

Target product:
CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21

Branch transformation:
COC(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21>>Cn1c(=O)n(CC(=O)O)c2nc(-c3ccccc3)ncc21

Interpretation:
- This branch identifies a carboxylate-containing purinone/purine-core precursor.
- It reflects a core-opening / ester-hydrolysis logic that is consistent with the scaffold architecture.
- Template SMARTS correspond to ester/acid interconversion logic.
- Reported model score: 0.26370516419410706
- Reported plausibility: 0.9969639778137207

Assessment:
- Chemically interpretable: yes
- Consistent with known AC-5216 scaffold strategy: partial

## Final classification

Classification: partial scaffold precedent recovered

Reason:
- The ASKCOS tree clearly recovers the desmethyl precursor / late methylation logic and the side-chain disconnection logic consistent with the known AC-5216 scaffold strategy.
- It does not reproduce the literature route exactly, and none of the returned branches are marked terminal or buyable, but the motifs are sufficiently coherent to support ASKCOS as a useful feasibility tool for scaffold-level guidance.
