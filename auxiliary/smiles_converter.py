from rdkit import Chem
from rdkit.Chem.rdMolDescriptors import CalcMolFormula

# Define the SMILES string (e.g., for caffeine)
smiles_string = 'CCN(Cc1c(F)ccc(OC)c1)C(=O)Cn2c3c(cnc(n3)c4ccccc4)n(c2=O)C(F)F'

# Convert the SMILES string to an RDKit molecule object
mol = Chem.MolFromSmiles(smiles_string)

# Check if the molecule object was created successfully
if mol is not None:
    # Calculate the molecular formula
    formula = CalcMolFormula(mol)
    print(f"SMILES: {smiles_string}")
    print(f"Chemical Formula: {formula}")
else:
    print(f"Error: Could not process SMILES string {smiles_string}")

