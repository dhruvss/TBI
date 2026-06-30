# 0) Packages
pkgs <- c("dplyr","tidyr","readr","stringr","ggplot2","ggrepel")
to_install <- pkgs[!sapply(pkgs, requireNamespace, quietly = TRUE)]
if(length(to_install)) install.packages(to_install, repos = "https://cloud.r-project.org")
invisible(lapply(pkgs, library, character.only = TRUE))

ok <- function(msg) cat("✓", msg, "\n")

# Resolve repository root from the location of this script
args_full <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args_full, value = TRUE)

if (length(file_arg) == 1) {
  script_path <- normalizePath(
    sub("^--file=", "", file_arg),
    winslash = "/",
    mustWork = TRUE
  )
  project_root <- normalizePath(
    file.path(dirname(script_path), ".."),
    winslash = "/",
    mustWork = TRUE
  )
} else {
  project_root <- normalizePath(".", winslash = "/", mustWork = TRUE)
}

data_dir <- file.path(project_root, "data_analysis")
docking_dir <- file.path(project_root, "docking")
figdir <- file.path(project_root, "figures")

physchem_path <- file.path(data_dir, "pet_physchem.csv")
metrics_path <- file.path(data_dir, "pet_metrics.csv")
docking_path <- file.path(docking_dir, "results.csv")

dir.create(figdir, showWarnings = FALSE, recursive = TRUE)

# 2) Load
physchem <- read_csv(physchem_path, na = c("unspecified","NA",""), show_col_types = FALSE)
metrics  <- read_csv(metrics_path,  na = c("unspecified","NA",""), show_col_types = FALSE)
dock     <- read_csv(docking_path,  na = c("unspecified","NA",""), show_col_types = FALSE)
ok("loaded CSVs")

# 3) Canonical tracer names
canon <- function(x){
  x %>%
    str_replace_all("\\s","") %>%
    str_replace_all("\\(R\\)-?PK11195","PK11195") %>%
    str_replace_all("^11C-?","") %>%
    str_replace_all("^18F-?","") %>%
    str_replace_all("^\\^11C,?","") %>%
    str_replace_all("^\\^18F,?","") %>%
    str_replace_all("PBR-?28","PBR28") %>%
    str_replace_all("PBR-?06","PBR06") %>%
    str_replace_all("PBR-?111","PBR111") %>%
    str_replace_all("GE-?180","GE-180") %>%
    str_replace_all("AC-?5216","AC-5216") %>%
    str_replace_all("DPA-?713","DPA-713") %>%
    str_replace_all("PK11195","PK11195")
}
# Ensure columns exist
for (nm in c("region","condition","genotype")) if (!nm %in% names(metrics)) metrics[[nm]] <- NA_character_

physchem <- physchem %>% mutate(tracer_c = canon(tracer))
metrics  <- metrics  %>% mutate(tracer_c = canon(tracer))
dock     <- dock     %>% mutate(tracer_c = canon(tracer))
ok("standardized tracer names")

# 4) Filter metrics to healthy/baseline; keep blockade-derived VND
keep_row <- function(cond) if (is.na(cond)) TRUE else !str_detect(cond, "(?i)\\bMS\\b|^ms_")
metrics_f <- metrics %>%
  filter(keep_row(condition)) %>%
  mutate(
    geno_rank = case_when(toupper(coalesce(genotype,""))=="HAB" ~ 1L, TRUE ~ 2L), # nolint
    region_rank = case_when(
      is.na(region) ~ 5L,
      region %in% c("global_mean","whole_brain") ~ 1L,
      region %in% c("mean_of_10_rois") ~ 2L,
      region %in% c("frontal_cortex","frontal","cortex") ~ 3L,
      TRUE ~ 4L
    ),
    value = suppressWarnings(as.numeric(value))
  ) %>% drop_na(value)

# pick one value per (tracer, metric)
metrics_pick <- metrics_f %>%
  arrange(tracer_c, metric, geno_rank, region_rank) %>%
  group_by(tracer_c, metric) %>%
  slice(1) %>% ungroup() %>%
  select(tracer_c, metric, value)
ok("selected per-tracer metrics")

# 5) Physchem subset (as provided)
physchem_pick <- physchem %>%
  transmute(
    tracer_c,
    mean_Ki_nM = suppressWarnings(as.numeric(mean_Ki_nM)),
    logD7.4    = suppressWarnings(as.numeric(`logD7.4`))
  ) %>% distinct(tracer_c, .keep_all = TRUE)

# 6) Docking energy
dock_pick <- dock %>%
  transmute(tracer_c, energy = suppressWarnings(as.numeric(energy))) %>%
  group_by(tracer_c) %>% slice(1) %>% ungroup()

# 7) Merge wide
wide <- full_join(
          physchem_pick,
          pivot_wider(metrics_pick, names_from = metric, values_from = value),
          by = "tracer_c"
        ) %>% full_join(dock_pick, by = "tracer_c")

study_tracers <- c("PK11195","DPA-713","PBR28","PBR06","PBR111","GE-180","AC-5216","DAA1106")
wide <- wide %>% filter(tracer_c %in% study_tracers)

# normalize fP to fraction if given as percent
if("fP" %in% names(wide) && any(!is.na(wide$fP))){
  if(max(wide$fP, na.rm = TRUE) > 1 && max(wide$fP, na.rm = TRUE) <= 100){
    wide <- wide %>% mutate(fP = fP/100)
  }
}
ok(paste("built wide table with", nrow(wide), "tracers"))

# 8) Z-scores (direction-aware)
zify <- function(x){
  if (all(is.na(x)) || is.na(sd(x, na.rm=TRUE)) || sd(x, na.rm=TRUE)==0) rep(NA_real_, length(x)) else as.numeric(scale(x))
}
wide <- wide %>%
  mutate(
    log10Ki    = if_else(!is.na(mean_Ki_nM), log10(mean_Ki_nM), NA_real_),
    z_Ki_inv   = zify(-log10Ki),
    z_VT       = zify(VT),
    z_BPND     = zify(BPND),
    z_VND_inv  = zify(-VND),
    z_fP       = zify(fP),
    z_VT_over_fP = zify(VT_over_fP),
    z_logD     = zify(logD7.4),
    z_dock_inv = zify(-energy)
  )

z_cols <- c("z_Ki_inv","z_VT","z_BPND","z_VND_inv","z_fP","z_VT_over_fP","z_logD","z_dock_inv")
wide <- wide %>%
  rowwise() %>%
  mutate(
    composite_mean = if (all(is.na(c_across(all_of(z_cols))))) NA_real_
                     else mean(c_across(all_of(z_cols)), na.rm = TRUE),
    composite_n    = sum(!is.na(c_across(all_of(z_cols))))
  ) %>% ungroup()
ok("computed z-scores + composite")

# 9) Save CSV + Figures to figures/
write_csv(wide, file.path(figdir, "pet_tracer_features_and_z.csv"))

leader <- wide %>% arrange(desc(composite_mean)) %>%
  mutate(rank=row_number(), tracer=factor(tracer_c, levels=rev(tracer_c)))
gg_leader <- ggplot(leader, aes(tracer, composite_mean)) +
  geom_col(width=0.7) +
  geom_text(aes(label=sprintf("#%d", rank)), hjust=-0.1, size=3.5) +
  coord_flip(clip="off") +
  labs(title="TSPO tracer leaderboard (composite z-score)", x=NULL, y="composite z") +
  theme_minimal(base_size=12) +
  theme(plot.margin = margin(10, 40, 10, 10), panel.grid.major.y = element_blank())
ggsave(file.path(figdir, "leaderboard_composite.png"), gg_leader, width=7.5, height=5.5, dpi=300)

scatter_dat <- wide %>% select(tracer_c, z_VT, z_BPND, z_dock_inv, composite_mean) %>%
  filter(!is.na(z_VT) | !is.na(z_BPND))
gg_scatter <- ggplot(scatter_dat, aes(x=z_VT, y=z_BPND, label=tracer_c)) +
  geom_point(aes(size=abs(z_dock_inv), color=composite_mean), alpha=0.9) +
  ggrepel::geom_text_repel(min.segment.length=0.1, box.padding=0.3, max.overlaps=20) +
  scale_size_continuous(name="|z_dock|", range=c(2,7)) +
  scale_color_viridis_c(name="composite z", option="C") +
  labs(title="Z-scores: VT vs BPND",
       x="z(VT)  (higher is better)", y="z(BPND)  (higher is better)") +
  theme_minimal(base_size=12) + theme(legend.position="right")
ggsave(file.path(figdir, "scatter_vt_vs_bpnd.png"), gg_scatter, width=7.5, height=5.5, dpi=300)

ok("saved CSV + figures to 'figures/'")
# Print leaderboard
wide %>% arrange(desc(composite_mean)) %>% select(tracer_c, composite_mean, composite_n) %>% print(n=Inf)
