# Created 2/15/2025 - AI was used to create this script with all final computations done by me and error correction done by me
# I proposed the original method after analyzing Turku PET Centre documentation and Lammertsma et al. - final method done based on Turku PET frameworks
# Prompt "give an R script that details VT and BPND (if possible) values based on the equations from Turku PET Centre's Logan plot documentation"
# "This should produce a linear regression plot showing dCt/Ct(t) vs dCp/Ct(t) with slope VT and int VND"
WD <- "/Users/dhruv/Documents/Research/TBI-tracer/data_analysis"
if (!dir.exists(WD)) stop("Working directory does not exist: ", WD)
setwd(WD)
message("Working dir set to: ", getwd())

# --------- 1) Packages ----------
ensure_pkg <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}
ensure_pkg("ggplot2")
suppressPackageStartupMessages(library(ggplot2))

# --------- 2) Output folders ----------
dir.create("outputs", showWarnings = FALSE)
dir.create(file.path("outputs", "figures"), showWarnings = FALSE, recursive = TRUE)
dir.create(file.path("outputs", "qc"), showWarnings = FALSE, recursive = TRUE)
dir.create(file.path("outputs", "fits"), showWarnings = FALSE, recursive = TRUE)

# --------- 3) User settings ----------
FIT_WINDOW_MIN <- 90

# Ct was checked at a suitably small value so dCt/dt is not large and clearly shows an increase based on the statistical logan plot
CT_EPS <- 1e-12

# Additional safeguard: drop tail points where Ct is extremely tiny relative to its peak
# (prevents artificial perfect linearity from dividing by tiny Ct).
CT_TAIL_FRACTION <- 1e-8  # Ct must be >= max(Ct)*this

# Distribution created with a critical value t* based on t(min) - independent variable that was changed for each run per analog
# Checked the VT stability across critical values in order to ensure VT was a reliable measure according to different timepoints
TSTAR_GRID <- seq(10, 40, by = 5)

# Candidate t* values for "auto" selection:
# defensible constraint: choose the EARLIEST t* whose fit is already very linear
# and VT is stable, instead of always picking the highest R² at the latest times.
TSTAR_AUTO_CAND <- seq(10, 40, by = 2.5)
AUTO_R2_MIN <- 0.98
AUTO_MIN_POINTS <- 8

# Robustness: warn if VT varies a lot across t* grid (relative range)
VT_SENS_WARN_FRAC <- 0.10  # 10%

read_mobi_table <- function(file) {
  df <- tryCatch(read.csv(file, check.names = FALSE), error = function(e) NULL)
  if (is.null(df)) stop("read.csv failed: ", file)
  if (ncol(df) == 1) {
    df2 <- tryCatch(read.delim(file, check.names = FALSE), error = function(e) NULL)
    if (!is.null(df2) && ncol(df2) > 1) df <- df2
  }
  df
}

# --------- 5) Core numeric helpers ----------
cumtrapz <- function(t, x) {
  n <- length(t)
  out <- rep(0, n)
  if (n < 2) return(out)
  for (i in 2:n) {
    out[i] <- out[i - 1] + (t[i] - t[i - 1]) * (x[i - 1] + x[i]) / 2
  }
  out
}

clean_series <- function(t_min, Cp, Ct) {
  ok <- is.finite(t_min) & is.finite(Cp) & is.finite(Ct)
  t_min <- t_min[ok]; Cp <- Cp[ok]; Ct <- Ct[ok]
  if (length(t_min) < 10) stop("Too few samples after cleaning (need >= 10).")

  ord <- order(t_min)
  t_min <- t_min[ord]; Cp <- Cp[ord]; Ct <- Ct[ord]

  # Collapse duplicate times via mean
  if (any(duplicated(t_min))) {
    df <- data.frame(t = t_min, Cp = Cp, Ct = Ct)
    agg <- aggregate(. ~ t, df, mean)
    t_min <- agg$t; Cp <- agg$Cp; Ct <- agg$Ct
  }

  if (any(diff(t_min) <= 0)) stop("Time not strictly increasing after cleaning.")
  list(t = t_min, Cp = Cp, Ct = Ct)
}

detect_cols <- function(nms) {
  time <- nms[nms == "Time [h]"]
  if (length(time) != 1) stop("Missing or non-unique Time [h].")

  cp <- nms[grepl("^ArterialBlood-.*Plasma", nms) & grepl("\\[µmol/l\\]", nms)]
  inter <- nms[grepl("^Brain-Interstitial-.*Concentration in container", nms) & grepl("\\[µmol/l\\]", nms)]
  intra <- nms[grepl("^Brain-Intracellular-.*Concentration in container", nms) & grepl("\\[µmol/l\\]", nms)]

  if (length(cp) < 1) stop("Missing arterial plasma Cp column.")
  if (length(inter) < 1) stop("Missing Brain-Interstitial column.")
  if (length(intra) < 1) stop("Missing Brain-Intracellular column.")

  pick <- function(x) x[order(nchar(x), decreasing = TRUE)][1]
  list(
    time = time,
    cp = pick(cp),
    inter = pick(inter),
    intra = pick(intra)
  )
}

# --------- 6) Logan calculations ----------
logan_xy <- function(t, Cp, Ct) {
  # Precondition: t sorted increasing, Ct > 0, Cp >= 0
  intCp <- cumtrapz(t, Cp)
  intCt <- cumtrapz(t, Ct)
  X <- intCp / Ct
  Y <- intCt / Ct
  list(X = X, Y = Y)
}

logan_fit_at_tstar <- function(t, X, Y, tstar) {
  idx <- which(t >= tstar & is.finite(X) & is.finite(Y))
  if (length(idx) < AUTO_MIN_POINTS) return(list(VT = NA_real_, intercept = NA_real_, r2 = NA_real_, n = length(idx)))
  fit <- lm(Y[idx] ~ X[idx])
  vt <- as.numeric(coef(fit)[2])
  r2 <- summary(fit)$r.squared
  list(VT = vt, intercept = as.numeric(coef(fit)[1]), r2 = r2, n = length(idx))
}

# Auto t* selection (more defensible than "max R²"):
# choose the earliest t* where (a) R² >= AUTO_R2_MIN and (b) slope is positive/finite
# and (c) VT is stable vs the next couple candidate t* (within VT_SENS_WARN_FRAC/2).
choose_tstar_auto <- function(t, X, Y, cand) {
  fits <- lapply(cand, function(ts) c(ts, unlist(logan_fit_at_tstar(t, X, Y, ts))))
  # fits rows: ts, VT, intercept, r2, n
  mat <- do.call(rbind, fits)
  colnames(mat) <- c("tstar", "VT", "intercept", "r2", "n")
  mat <- as.data.frame(mat)

  # basic validity
  good <- is.finite(mat$VT) & mat$VT > 0 & is.finite(mat$r2) & mat$r2 >= AUTO_R2_MIN & mat$n >= AUTO_MIN_POINTS
  if (!any(good)) {
    # fallback: pick best r2 among valid VT>0
    good2 <- is.finite(mat$VT) & mat$VT > 0 & is.finite(mat$r2) & mat$n >= AUTO_MIN_POINTS
    if (!any(good2)) return(list(tstar = NA_real_, VT = NA_real_, r2 = NA_real_, note = "No valid t* fit found."))
    k <- which.max(mat$r2[good2])
    idx <- which(good2)[k]
    return(list(tstar = mat$tstar[idx], VT = mat$VT[idx], r2 = mat$r2[idx], note = "Fallback: max R2 among valid."))
  }

  # pick earliest "good" that is stable vs next two candidates
  good_idx <- which(good)
  for (i in good_idx) {
    vt_i <- mat$VT[i]
    # compare against next two candidate entries (if they exist)
    next_idx <- which(mat$tstar > mat$tstar[i])[1:2]
    next_idx <- next_idx[is.finite(next_idx)]
    if (length(next_idx) == 0) {
      return(list(tstar = mat$tstar[i], VT = vt_i, r2 = mat$r2[i], note = "Auto: earliest good (no later checks)."))
    }
    vt_next <- mat$VT[next_idx]
    vt_next <- vt_next[is.finite(vt_next) & vt_next > 0]
    if (length(vt_next) == 0) next
    rel_diff <- max(abs(vt_next - vt_i) / vt_i)
    if (is.finite(rel_diff) && rel_diff <= (VT_SENS_WARN_FRAC / 2)) {
      return(list(tstar = mat$tstar[i], VT = vt_i, r2 = mat$r2[i], note = "Auto: earliest good + stable."))
    }
  }

  # if none stable, still pick earliest good
  i <- good_idx[1]
  list(tstar = mat$tstar[i], VT = mat$VT[i], r2 = mat$r2[i], note = "Auto: earliest good (stability not met).")
}

# --------- 7) Main batch ----------
csv_files <- list.files(pattern = "^A\\d+\\.csv$", full.names = TRUE)
if (length(csv_files) == 0) stop("No A#.csv files found in: ", getwd())

master_rows <- list()

for (file in csv_files) {
  analog_id <- sub("\\.csv$", "", basename(file))
  message("\n--- Processing ", analog_id, " ---")

  cols_used <- list(cp = "", inter = "", intra = "")

  res_row <- tryCatch({
    df <- read_mobi_table(file)
    cols <- detect_cols(colnames(df))
    cols_used <- cols

    # read and build curves
    t_min_raw <- as.numeric(df[[cols$time]]) * 60
    Cp_raw <- as.numeric(df[[cols$cp]])
    Ct_raw <- as.numeric(df[[cols$inter]]) + as.numeric(df[[cols$intra]])

    cleaned <- clean_series(t_min_raw, Cp_raw, Ct_raw)

    # restrict to fit window
    keepw <- which(cleaned$t <= FIT_WINDOW_MIN)
    t <- cleaned$t[keepw]
    Cp <- cleaned$Cp[keepw]
    Ct <- cleaned$Ct[keepw]

    # filter out early zeros and tiny tail Ct that causes blow-ups
    ct_peak <- max(Ct, na.rm = TRUE)
    ct_tail_eps <- max(CT_EPS, ct_peak * CT_TAIL_FRACTION)
    keep_ct <- which(is.finite(Ct) & Ct > ct_tail_eps & is.finite(Cp) & Cp >= 0)
    if (length(keep_ct) < 12) stop("Too few Ct>threshold points after filtering. Lower CT_EPS or CT_TAIL_FRACTION.")

    t2 <- t[keep_ct]; Cp2 <- Cp[keep_ct]; Ct2 <- Ct[keep_ct]

    # compute Logan X,Y
    xy <- logan_xy(t2, Cp2, Ct2)
    X <- xy$X; Y <- xy$Y

    # sensitivity across fixed t*
    sens <- data.frame(analog_id = analog_id, tstar = TSTAR_GRID, VT = NA_real_, r2 = NA_real_, n = NA_integer_)
    for (i in seq_along(TSTAR_GRID)) {
      fit <- logan_fit_at_tstar(t2, X, Y, TSTAR_GRID[i])
      sens$VT[i] <- fit$VT
      sens$r2[i] <- fit$r2
      sens$n[i] <- fit$n
    }
    write.csv(sens, file.path("outputs", "qc", paste0(analog_id, "_VT_by_tstar.csv")), row.names = FALSE)

    # auto t*
    auto <- choose_tstar_auto(t2, X, Y, TSTAR_AUTO_CAND)

    # compute warning flag for sensitivity
    vt_ok <- sens$VT[is.finite(sens$VT) & sens$VT > 0]
    vt_warn <- NA
    if (length(vt_ok) >= 3) {
      rel_rng <- (max(vt_ok) - min(vt_ok)) / median(vt_ok)
      vt_warn <- is.finite(rel_rng) && rel_rng > VT_SENS_WARN_FRAC
    }

    # QC plot (Logan points)
    d <- data.frame(t = t2, X = X, Y = Y)
    d <- d[is.finite(d$X) & is.finite(d$Y), ]

    p <- ggplot(d, aes(x = X, y = Y)) +
      geom_point(size = 1.2) +
      geom_vline(xintercept = NA_real_) +
      labs(
        title = paste0(
          analog_id, " Logan VT (auto t*) = ", signif(auto$VT, 6),
          " | t*=", auto$tstar, " | R2=", signif(auto$r2, 6)
        ),
        subtitle = paste0(
          "Ct filter: > ", signif(ct_tail_eps, 3),
          " (max(Ct)*", CT_TAIL_FRACTION, ", CT_EPS=", CT_EPS, "). ",
          "Auto note: ", auto$note,
          ifelse(isTRUE(vt_warn), " | WARNING: VT varies >10% across t* grid.", "")
        ),
        x = "X(t) = (Area under Cp up to t) / Ct(t)",
        y = "Y(t) = (Area under Ct up to t) / Ct(t)"
      ) +
      theme_minimal(base_size = 12)

    ggsave(file.path("outputs", "figures", paste0(analog_id, "_logan_vt.png")),
           p, width = 6.8, height = 5.2, dpi = 220)

    # also save time-series QC so you can see Ct thresholds
    qc_ts <- data.frame(
      t_min = t,
      Cp = Cp,
      Ct_extrav = Ct,
      Ct_keep = Ct > ct_tail_eps
    )
    write.csv(qc_ts, file.path("outputs", "qc", paste0(analog_id, "_timeseries_qc.csv")), row.names = FALSE)

    # choose "reported VT" as auto VT; also record VT at each t*
    data.frame(
      analog_id = analog_id,
      cp_header = cols$cp,
      ct_header = paste0(cols$inter, " + ", cols$intra),
      fit_window_min = max(t, na.rm = TRUE),

      VT = auto$VT,
      tstar_min = auto$tstar,
      r2 = auto$r2,
      auto_note = auto$note,

      ct_eps = CT_EPS,
      ct_tail_fraction = CT_TAIL_FRACTION,
      ct_tail_eps = ct_tail_eps,

      vt_sensitivity_warn = vt_warn,
      VT_tstar10 = sens$VT[sens$tstar == 10],
      VT_tstar15 = sens$VT[sens$tstar == 15],
      VT_tstar20 = sens$VT[sens$tstar == 20],
      VT_tstar25 = sens$VT[sens$tstar == 25],
      VT_tstar30 = sens$VT[sens$tstar == 30],
      VT_tstar35 = sens$VT[sens$tstar == 35],
      VT_tstar40 = sens$VT[sens$tstar == 40],

      error = "",
      row.names = NULL
    )
  }, error = function(e) {
    data.frame(
      analog_id = analog_id,
      cp_header = cols_used$cp,
      ct_header = if (nzchar(cols_used$inter) && nzchar(cols_used$intra)) paste0(cols_used$inter, " + ", cols_used$intra) else "",
      fit_window_min = FIT_WINDOW_MIN,

      VT = NA_real_,
      tstar_min = NA_real_,
      r2 = NA_real_,
      auto_note = "",

      ct_eps = CT_EPS,
      ct_tail_fraction = CT_TAIL_FRACTION,
      ct_tail_eps = NA_real_,

      vt_sensitivity_warn = NA,
      VT_tstar10 = NA_real_, VT_tstar15 = NA_real_, VT_tstar20 = NA_real_,
      VT_tstar25 = NA_real_, VT_tstar30 = NA_real_, VT_tstar35 = NA_real_,
      VT_tstar40 = NA_real_,

      error = conditionMessage(e),
      row.names = NULL
    )
  })

  write.csv(res_row, file.path("outputs", "fits", paste0(analog_id, "_logan_vt_results.csv")), row.names = FALSE)
  master_rows[[analog_id]] <- res_row
}

master <- do.call(rbind, master_rows)
write.csv(master, file.path("outputs", "MASTER_VT_logan_with_sensitivity.csv"), row.names = FALSE)

message("\nDone.")
message("MASTER: outputs/MASTER_VT_logan_with_sensitivity.csv")
message("Per-analog plots: outputs/figures/*_logan_vt.png")
message("Per-analog sensitivity: outputs/qc/*_VT_by_tstar.csv")
message("Per-analog time-series QC: outputs/qc/*_timeseries_qc.csv")
