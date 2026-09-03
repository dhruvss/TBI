# ASKCOS-predicted retrosynthetic routes for AC-5216

This benchmark used the public ASKCOS MCTS endpoint at https://askcos.mit.edu/api/tree-search/mcts/call-sync-without-token with the target SMILES:

CCN(Cc1ccccc1)C(=O)Cn1c(=O)n(C)c2cnc(-c3ccccc3)nc21

The live API returned a tree with 200 candidate pathways and a successful MCTS execution message, but no pathway in the returned result reached a terminal node marked as complete/buyable. In other words, the ASKCOS response captured a large search tree and reaction candidates, but no complete retrosynthetic route was present in the raw path output that could be summarized as a completed path.

## Route status

- ASKCOS execution status: successful
- Number of returned pathways: 200
- Number of complete routes found: 0
- Interpretation: the tree contains many reaction expansions and precursor candidates, but the returned graph does not include a terminal, complete, route-terminated leaf that can be treated as a finished retrosynthetic route for manual extraction.

## Observed route structure

The returned graph contains reaction nodes corresponding to plausible retro-transformations such as:

- cleavage of the N-methyl amide/urea-like motif to propose `CCNCc1ccccc1` plus an N-methylated cyclic precursor;
- N-methylation reversal to propose a de-methylated precursor and methyl iodide;
- a bicyclic heterocycle precursor of the form `Cn1c(=O)n(CC(=O)O)c2nc(-c3ccccc3)ncc21`.

These are ASKCOS-predicted retrosynthetic fragments, not yet independently validated as chemically complete or synthetically realistic routes.

## Important note

This is not a declaration of synthetic validity or literature agreement. It is a raw ASKCOS tree-search output, and the raw route set requires manual inspection before any forward-validation or synthetic claim is made.
