# RAN IN MANUAL PYMOL WORKFLOW - NOT USED IN FINAL ANALYSIS, REF ONLY
# Render TSPO docking poses in space-filling style
# Run with: pymol -cq ~/Documents/Research/TBI-tracer/render_spacefill.py

# import os, glob, sys
from pathlib import Path

# ---------- CONFIG ----------
#DOCK_DIR   = os.path.expanduser("~/Documents/Research/TBI-tracer/docking")
#OUT_DIR    = os.path.expanduser("~/Documents/Research/TBI-tracer/figures/poses")
#POSE_MODE  = "top"   # "top" = first state only,  "all" = render every pose state
# Visual style toggles
#SURFACE_PROTEIN__SPHERES_LIGAND = True  # True = protein surface + ligand spheres; False = spheres for both
#PROT_SURF_TRANSP = 0.35   # protein surface transparency (0 = opaque, 1 = invisible)
#PROT_SPHERE_SCALE = 0.30  # if using spheres for protein
#LIG_SPHERE_SCALE  = 0.75  # ligand sphere size

# Image settings
#IMG_W, IMG_H, IMG_DPI = 1800, 1400, 300

# Files to skip as "ligands"
#SKIP_NAMES = {
    #"TSPO_receptor.pdbqt", "TSPO_receptor.pdb",
    #"TSPO_prepped.pdbqt", "TSPO_prepped.pdb",
    #"4uc1.pdbqt", "4uc1.pdb",
   # "Human_TSPO.pdbqt", "Human_TSPO.pdb"


# ---------- FIND RECEPTOR ----------
#CANDIDATES = [
    #"TSPO_receptor.pdbqt", "TSPO_receptor.pdb",
    #"TSPO_prepped.pdbqt", "TSPO_prepped.pdb",
    #"4uc1.pdb", "4uc1.pdbqt",
    #Human_TSPO.pdbqt", "Human_TSPO.pdb"

#receptor_path = None
#for c in CANDIDATES:
    #p = os.path.join(DOCK_DIR, c)
    #if os.path.exists(p):
        #receptor_path = p
        #break
#if receptor_path is None:
    #sys.stderr.write("ERROR: No receptor found in docking dir. Looked for: %s\n" % ", ".join(CANDIDATES))
    #sys.exit(1)

# ---------- BOOT PYMOL ----------
#import pymol
#from pymol import cmd, util
#pymol.finish_launching(['pymol','-q'])  # quiet

# Make sure output dir exists
#Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

# ---------- GLOB LIGANDS ----------
#lig_paths = sorted(glob.glob(os.path.join(DOCK_DIR, "*.pdbqt")))
#lig_paths = [p for p in lig_paths if os.path.basename(p) not in SKIP_NAMES]
#if not lig_paths:
    #sys.stderr.write("No ligand PDBQT files found in: %s\n" % DOCK_DIR)
    #sys.exit(1)

# ---------- RENDER LOOP ----------
#for lig_path in lig_paths:
    #base = os.path.basename(lig_path)
    #name = os.path.splitext(base)[0]

    #cmd.reinitialize()
    #cmd.bg_color("white")
    #cmd.set("ray_shadows", "off")
    #cmd.set("antialias", 2)
    #cmd.set("depth_cue", 0)

    # Load receptor + ligand
    #cmd.load(receptor_path, "rec")
    #cmd.load(lig_path, "lig")

    # Determine number of states (poses) for ligand
#n_states = int(cmd.count_states("lig"))
    #states_to_render = [1] if (POSE_MODE.lower() == "top" or n_states <= 1) else list(range(1, n_states+1))

    #for st in states_to_render:
        # Show specific pose
        #cmd.frame(st)
        # Clean scene
        #cmd.hide("everything", "all")

        #if SURFACE_PROTEIN__SPHERES_LIGAND:
            # Protein as surface (space-filling-ish), semi-transparent
            #cmd.show("surface", "rec")
            #cmd.set("transparency", PROT_SURF_TRANSP, "rec")
            #cmd.color("gray80", "rec")
        #else:
            # Both as spheres (pure space-fill)
            #cmd.show("spheres", "rec")
            #cmd.set("sphere_scale", PROT_SPHERE_SCALE, "rec")
            #cmd.color("gray80", "rec")

        # Ligand as spheres
        #cmd.show("spheres", "lig")
        #cmd.set("sphere_scale", LIG_SPHERE_SCALE, "lig")
        #cmd.color("tv_orange", "lig")
        # Optional: color by element (uncomment next line if preferred)
        # util.cbag("lig")  # carbon blue/green mixed scheme, or util.cnc for cyan carbons, etc.

        # Focus and render
        #cmd.orient("lig")
        #cmd.zoom("lig", 10)

        # Output name
        #if len(states_to_render) == 1:
            #out_png = os.path.join(OUT_DIR, f"{name}_spacefill.png")
        #else:
            #out_png = os.path.join(OUT_DIR, f"{name}_pose{st:02d}_spacefill.png")

        #cmd.png(out_png, width=IMG_W, height=IMG_H, dpi=IMG_DPI, ray=1)
        #print(f"✓ Wrote {out_png}")

# Optional: also save a .pse session of the last scene
# cmd.save(os.path.join(OUT_DIR, "last_render.pse"))
