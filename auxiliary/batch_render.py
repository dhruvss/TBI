# SCRIPT FULLY DONE THROUGH PYMOL GUI, NOT USED IN FINAL ANALYSIS, KEPT FOR REFERENCE ONLY

#from pymol import cmd, finish_launching
#import os, sys

# ===== Launch =====
# print('>>> batch_render.py starting')
# Launch PyMOL quietly (no GUI)
# finish_launching(['pymol', '-qc'])

# ===== Paths =====
# #PROJECT_ROOT = "/Users/dhruv/Documents/Research/TBI-tracer"
# DOCK_DIR = os.path.join(PROJECT_ROOT, 'docking')
# FIG_DIR = os.path.join(PROJECT_ROOT, 'figures')

# Diagnostics: show what's in docking/
# try:
    #dock_files = os.listdir(DOCK_DIR)
    #print('DOCK_DIR contents:', dock_files)
#except Exception as e:
   #print(f'Error reading docking directory: {e}')
    #sys.exit(1)

# os.makedirs(FIG_DIR, exist_ok=True)

# ===== Loop =====
# count = 0
# for filename in dock_files:
    # if not filename.endswith('_out.pdbqt'):
        # continue
    #count += 1
    # name = filename[:-9]  # strip suffix
    # print(f'-- Rendering pose for: {name}')

    # Clear previous objects
    # cmd.delete('all')

    # Load structures
    # cmd.load(os.path.join(DOCK_DIR, 'TSPO_receptor.pdbqt'), 'receptor')
    # cmd.load(os.path.join(DOCK_DIR, filename), 'ligand')

    # Style
    # cmd.show('cartoon', 'receptor')
   # cmd.color('slate', 'receptor')
    # cmd.show('sticks', 'ligand')
    # cmd.color('yellow', 'ligand')

    # View
    # cmd.zoom('all', 8)
    # cmd.bg_color('white')

    # Render
    # cmd.ray(1200, 800)
    # out_png = os.path.join(FIG_DIR, f"{name}_pose.png")
    # cmd.png(out_png, dpi=300)
    # print(f'---- Saved {out_png}')

# if count == 0:
    # print('Warning: no *_out.pdbqt files found—nothing rendered.')

# cmd.quit()
