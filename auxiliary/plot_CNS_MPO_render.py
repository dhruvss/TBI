import plotly.express as px
import pandas as pd
import numpy as np

num_points = 1923
df = pd.read_csv('~/Documents/Research/TBI-tracer/data_analysis/enum_figure_3Dvis.csv')

lead_ids = ["emap_Bn-4OCF3_Me", 
            "emap_Bn-4OCHF2_Me", 
            "emap2_Bn_CH2CF3", 
            "emap2_Bn-4F_Me",
             "emap2_Bn-3,5diF_CH2CH2F",
             "emap2_Bn-3,4diF_Me",
             "emap2_Bn-3,4diF_CHF2",
             "emap2_Bn-3,4diCl_Me",
             "emap2_Bn-4OCF3_Me",
             "emap2_Bn-4OMe_CH2CF3",
             "emap3_Bn_OCH2CF3",
             "emap3_Bn-3F_CH2CH2CF3",
             "emap3_Bn-3Cl_CH2F",
             "emap3_Bn-3,5diF_nPr",
             "emap3_Bn-3,4diCl_Me",
             "emap3_Bn-3F_4OMe_CH2CHF2",
             "emap3_Bn-3CF3_4F_Me",
             "AC5216_ref"]
df['Status'] = 'Other'
df.loc[df['ligand_id'].isin(lead_ids), 'Status'] = 'Lead'

# Create the interactive 3D scatter plot
X = 'logD7.4_est'
Y = 'TPSA'
Z = 'E_dock'
fig = px.scatter_3d(
    df,
    x=X,
    y=Y,
    z=Z,
    color='Status',                # Colors points by Lead vs Other
    color_discrete_map={           # Explicitly set the colors
        'Lead': 'red', 
        'Other': 'lightblue'
    },
    opacity=0.8,
    title="CNS MPO Properties vs. Docking Energy - Leads Highlighted",
    hover_data=['ligand_id']   # Shows the ID when you hover over a point
)
# Show the figure (this will open an interactive plot in your browser or Jupyter notebook)
fig.show()

