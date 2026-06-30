# src/11_MoBi_turku_logan_fits.R
#
# Created 2/15/2025.
# AI was used to help draft the original script; final computations,
# methodological decisions, and error correction were completed by the author.
#
# The method was developed after reviewing Turku PET Centre documentation
# and Lammertsma et al. The script estimates relative Logan VT values from
# simulated arterial plasma and brain concentration-time curves.

# --------- 0) Resolve repository paths ----------

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
  # Fallback for interactive sourcing.
  project_root <- normalizePath(
    ".",
    winslash = "/",
    mustWork = TRUE
  )
}

data_analysis_dir <- file.path(project_root, "data_analysis")

# Raw A#.csv TAC files currently live here in the repository.
input_dir <- file.path(data_analysis_dir, "outputs")

# Analysis products are also retained under data_analysis/outputs.
output_dir <- file.path(data_analysis_dir, "outputs")
figures_dir <- file.path(output_dir, "figures")
qc_dir <- file.path(output_dir, "qc")
fits_dir <- file.path(output_dir, "fits")

if (!dir.exists(data_analysis_dir)) {
  stop("Missing data-analysis directory: ", data_analysis_dir)
}

if (!dir.exists(input_dir)) {
  stop("Missing Logan input directory: ", input_dir)
}

message("Repository root: ", project_root)
message("Input directory: ", input_dir)
message("Output directory: ", output_dir)

# --------- 1) Packages ----------

ensure_pkg <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}

ensure_pkg("ggplot2")

suppressPackageStartupMessages(
  library(ggplot2)
)

# --------- 2) Output folders ----------

dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(figures_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(qc_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(fits_dir, showWarnings = FALSE, recursive = TRUE)

# --------- 3) User settings ----------

FIT_WINDOW_MIN <- 90

# Ct was checked at a suitably small value so dCt/dt is not large and
# clearly shows an increase based on the statistical Logan plot.
CT_EPS <- 1e-12

# Additional safeguard: drop tail points where Ct is extremely tiny
# relative to its peak. This prevents artificial linearity caused by
# division by very small Ct values.
CT_TAIL_FRACTION <- 1e-8

# Distribution created with a critical value t* based on t(min).
# VT stability was evaluated across several critical values.
TSTAR_GRID <- seq(10, 40, by = 5)

# Candidate t* values for automatic selection.
# Select the earliest t* with a sufficiently linear and stable fit rather
# than automatically selecting the latest fit with the largest R-squared.
TSTAR_AUTO_CAND <- seq(10, 40, by = 2.5)
AUTO_R2_MIN <- 0.98
AUTO_MIN_POINTS <- 8

# Warn when VT varies substantially across the fixed t* grid.
VT_SENS_WARN_FRAC <- 0.10

# --------- 4) Input reader ----------

read_mobi_table <- function(file) {
  df <- tryCatch(
    read.csv(file, check.names = FALSE),
    error = function(e) NULL
  )

  if (is.null(df)) {
    stop("read.csv failed: ", file)
  }

  if (ncol(df) == 1) {
    df2 <- tryCatch(
      read.delim(file, check.names = FALSE),
      error = function(e) NULL
    )

    if (!is.null(df2) && ncol(df2) > 1) {
      df <- df2
    }
  }

  df
}

# --------- 5) Core numeric helpers ----------

cumtrapz <- function(t, x) {
  n <- length(t)
  out <- rep(0, n)

  if (n < 2) {
    return(out)
  }

  for (i in 2:n) {
    out[i] <- out[i - 1] +
      (t[i] - t[i - 1]) * (x[i - 1] + x[i]) / 2
  }

  out
}

clean_series <- function(t_min, Cp, Ct) {
  ok <- is.finite(t_min) & is.finite(Cp) & is.finite(Ct)

  t_min <- t_min[ok]
  Cp <- Cp[ok]
  Ct <- Ct[ok]

  if (length(t_min) < 10) {
    stop("Too few samples after cleaning; at least 10 are required.")
  }

  ord <- order(t_min)

  t_min <- t_min[ord]
  Cp <- Cp[ord]
  Ct <- Ct[ord]

  # Collapse duplicate time points using their mean values.
  if (any(duplicated(t_min))) {
    df <- data.frame(
      t = t_min,
      Cp = Cp,
      Ct = Ct
    )

    agg <- aggregate(. ~ t, df, mean)

    t_min <- agg$t
    Cp <- agg$Cp
    Ct <- agg$Ct
  }

  if (any(diff(t_min) <= 0)) {
    stop("Time is not strictly increasing after cleaning.")
  }

  list(
    t = t_min,
    Cp = Cp,
    Ct = Ct
  )
}

detect_cols <- function(nms) {
  time <- nms[nms == "Time [h]"]

  if (length(time) != 1) {
    stop("Missing or non-unique Time [h] column.")
  }

  cp <- nms[
    grepl("^ArterialBlood-.*Plasma", nms) &
      grepl("\\[µmol/l\\]", nms)
  ]

  inter <- nms[
    grepl(
      "^Brain-Interstitial-.*Concentration in container",
      nms
    ) &
      grepl("\\[µmol/l\\]", nms)
  ]

  intra <- nms[
    grepl(
      "^Brain-Intracellular-.*Concentration in container",
      nms
    ) &
      grepl("\\[µmol/l\\]", nms)
  ]

  if (length(cp) < 1) {
    stop("Missing arterial plasma Cp column.")
  }

  if (length(inter) < 1) {
    stop("Missing Brain-Interstitial column.")
  }

  if (length(intra) < 1) {
    stop("Missing Brain-Intracellular column.")
  }

  pick <- function(x) {
    x[order(nchar(x), decreasing = TRUE)][1]
  }

  list(
    time = time,
    cp = pick(cp),
    inter = pick(inter),
    intra = pick(intra)
  )
}

# --------- 6) Logan calculations ----------

logan_xy <- function(t, Cp, Ct) {
  # Preconditions:
  # t must be sorted in increasing order.
  # Ct must be positive.
  # Cp must be nonnegative.

  intCp <- cumtrapz(t, Cp)
  intCt <- cumtrapz(t, Ct)

  X <- intCp / Ct
  Y <- intCt / Ct

  list(
    X = X,
    Y = Y
  )
}

logan_fit_at_tstar <- function(t, X, Y, tstar) {
  idx <- which(
    t >= tstar &
      is.finite(X) &
      is.finite(Y)
  )

  if (length(idx) < AUTO_MIN_POINTS) {
    return(
      list(
        VT = NA_real_,
        intercept = NA_real_,
        r2 = NA_real_,
        n = length(idx)
      )
    )
  }

  fit <- lm(Y[idx] ~ X[idx])

  vt <- as.numeric(coef(fit)[2])
  intercept <- as.numeric(coef(fit)[1])
  r2 <- summary(fit)$r.squared

  list(
    VT = vt,
    intercept = intercept,
    r2 = r2,
    n = length(idx)
  )
}

# Choose the earliest t* where:
# 1. R-squared meets the minimum;
# 2. the VT slope is positive and finite;
# 3. VT is stable relative to the next candidate t* values.
choose_tstar_auto <- function(t, X, Y, cand) {
  fits <- lapply(
    cand,
    function(ts) {
      c(
        ts,
        unlist(
          logan_fit_at_tstar(t, X, Y, ts)
        )
      )
    }
  )

  # Rows contain:
  # tstar, VT, intercept, r2, n
  mat <- do.call(rbind, fits)

  colnames(mat) <- c(
    "tstar",
    "VT",
    "intercept",
    "r2",
    "n"
  )

  mat <- as.data.frame(mat)

  good <- is.finite(mat$VT) &
    mat$VT > 0 &
    is.finite(mat$r2) &
    mat$r2 >= AUTO_R2_MIN &
    mat$n >= AUTO_MIN_POINTS

  if (!any(good)) {
    # Fallback: select the best R-squared among valid positive VT fits.
    good2 <- is.finite(mat$VT) &
      mat$VT > 0 &
      is.finite(mat$r2) &
      mat$n >= AUTO_MIN_POINTS

    if (!any(good2)) {
      return(
        list(
          tstar = NA_real_,
          VT = NA_real_,
          r2 = NA_real_,
          note = "No valid t* fit found."
        )
      )
    }

    k <- which.max(mat$r2[good2])
    idx <- which(good2)[k]

    return(
      list(
        tstar = mat$tstar[idx],
        VT = mat$VT[idx],
        r2 = mat$r2[idx],
        note = "Fallback: max R2 among valid."
      )
    )
  }

  # Select the earliest good fit that remains stable relative to the next
  # two candidate t* values.
  good_idx <- which(good)

  for (i in good_idx) {
    vt_i <- mat$VT[i]

    next_idx <- which(mat$tstar > mat$tstar[i])[1:2]
    next_idx <- next_idx[is.finite(next_idx)]

    if (length(next_idx) == 0) {
      return(
        list(
          tstar = mat$tstar[i],
          VT = vt_i,
          r2 = mat$r2[i],
          note = "Auto: earliest good (no later checks)."
        )
      )
    }

    vt_next <- mat$VT[next_idx]
    vt_next <- vt_next[
      is.finite(vt_next) &
        vt_next > 0
    ]

    if (length(vt_next) == 0) {
      next
    }

    rel_diff <- max(
      abs(vt_next - vt_i) / vt_i
    )

    if (
      is.finite(rel_diff) &&
        rel_diff <= (VT_SENS_WARN_FRAC / 2)
    ) {
      return(
        list(
          tstar = mat$tstar[i],
          VT = vt_i,
          r2 = mat$r2[i],
          note = "Auto: earliest good + stable."
        )
      )
    }
  }

  # If none of the good fits meet the stability criterion,
  # retain the earliest otherwise acceptable fit.
  i <- good_idx[1]

  list(
    tstar = mat$tstar[i],
    VT = mat$VT[i],
    r2 = mat$r2[i],
    note = "Auto: earliest good (stability not met)."
  )
}

# --------- 7) Main batch ----------

csv_files <- list.files(
  path = input_dir,
  pattern = "^A\\d+\\.csv$",
  full.names = TRUE
)

if (length(csv_files) == 0) {
  stop(
    "No A#.csv files found in input directory: ",
    input_dir
  )
}

message(
  "Found ",
  length(csv_files),
  " analog TAC file(s)."
)

master_rows <- list()

for (file in csv_files) {
  analog_id <- sub(
    "\\.csv$",
    "",
    basename(file)
  )

  message(
    "\n--- Processing ",
    analog_id,
    " ---"
  )

  cols_used <- list(
    cp = "",
    inter = "",
    intra = ""
  )

  res_row <- tryCatch({
    df <- read_mobi_table(file)
    cols <- detect_cols(colnames(df))
    cols_used <- cols

    # Read and build curves.
    t_min_raw <- as.numeric(
      df[[cols$time]]
    ) * 60

    Cp_raw <- as.numeric(
      df[[cols$cp]]
    )

    Ct_raw <- as.numeric(
      df[[cols$inter]]
    ) + as.numeric(
      df[[cols$intra]]
    )

    cleaned <- clean_series(
      t_min_raw,
      Cp_raw,
      Ct_raw
    )

    # Restrict to the selected fit window.
    keepw <- which(
      cleaned$t <= FIT_WINDOW_MIN
    )

    t <- cleaned$t[keepw]
    Cp <- cleaned$Cp[keepw]
    Ct <- cleaned$Ct[keepw]

    # Remove early zero values and extremely small tail Ct values that
    # could produce unstable ratios.
    ct_peak <- max(
      Ct,
      na.rm = TRUE
    )

    ct_tail_eps <- max(
      CT_EPS,
      ct_peak * CT_TAIL_FRACTION
    )

    keep_ct <- which(
      is.finite(Ct) &
        Ct > ct_tail_eps &
        is.finite(Cp) &
        Cp >= 0
    )

    if (length(keep_ct) < 12) {
      stop(
        paste0(
          "Too few Ct-above-threshold points after filtering. ",
          "Lower CT_EPS or CT_TAIL_FRACTION."
        )
      )
    }

    t2 <- t[keep_ct]
    Cp2 <- Cp[keep_ct]
    Ct2 <- Ct[keep_ct]

    # Compute Logan X and Y.
    xy <- logan_xy(
      t2,
      Cp2,
      Ct2
    )

    X <- xy$X
    Y <- xy$Y

    # Sensitivity analysis across fixed t* values.
    sens <- data.frame(
      analog_id = analog_id,
      tstar = TSTAR_GRID,
      VT = NA_real_,
      r2 = NA_real_,
      n = NA_integer_
    )

    for (i in seq_along(TSTAR_GRID)) {
      fit <- logan_fit_at_tstar(
        t2,
        X,
        Y,
        TSTAR_GRID[i]
      )

      sens$VT[i] <- fit$VT
      sens$r2[i] <- fit$r2
      sens$n[i] <- fit$n
    }

    write.csv(
      sens,
      file.path(
        qc_dir,
        paste0(
          analog_id,
          "_VT_by_tstar.csv"
        )
      ),
      row.names = FALSE
    )

    # Automatically select t*.
    auto <- choose_tstar_auto(
      t2,
      X,
      Y,
      TSTAR_AUTO_CAND
    )

    # Determine whether VT is sensitive to the selected t*.
    vt_ok <- sens$VT[
      is.finite(sens$VT) &
        sens$VT > 0
    ]

    vt_warn <- NA

    if (length(vt_ok) >= 3) {
      rel_rng <- (
        max(vt_ok) - min(vt_ok)
      ) / median(vt_ok)

      vt_warn <- is.finite(rel_rng) &&
        rel_rng > VT_SENS_WARN_FRAC
    }

    # Logan QC plot.
    d <- data.frame(
      t = t2,
      X = X,
      Y = Y
    )

    d <- d[
      is.finite(d$X) &
        is.finite(d$Y),
    ]

    p <- ggplot(
      d,
      aes(
        x = X,
        y = Y
      )
    ) +
      geom_point(size = 1.2) +
      geom_vline(xintercept = NA_real_) +
      labs(
        title = paste0(
          analog_id,
          " Logan VT (auto t*) = ",
          signif(auto$VT, 6),
          " | t*=",
          auto$tstar,
          " | R2=",
          signif(auto$r2, 6)
        ),
        subtitle = paste0(
          "Ct filter: > ",
          signif(ct_tail_eps, 3),
          " (max(Ct)*",
          CT_TAIL_FRACTION,
          ", CT_EPS=",
          CT_EPS,
          "). Auto note: ",
          auto$note,
          ifelse(
            isTRUE(vt_warn),
            " | WARNING: VT varies >10% across t* grid.",
            ""
          )
        ),
        x = "X(t) = (Area under Cp up to t) / Ct(t)",
        y = "Y(t) = (Area under Ct up to t) / Ct(t)"
      ) +
      theme_minimal(base_size = 12)

    ggsave(
      filename = file.path(
        figures_dir,
        paste0(
          analog_id,
          "_logan_vt.png"
        )
      ),
      plot = p,
      width = 6.8,
      height = 5.2,
      dpi = 220
    )

    # Save time-series QC so the retained Ct values can be inspected.
    qc_ts <- data.frame(
      t_min = t,
      Cp = Cp,
      Ct_extrav = Ct,
      Ct_keep = Ct > ct_tail_eps
    )

    write.csv(
      qc_ts,
      file.path(
        qc_dir,
        paste0(
          analog_id,
          "_timeseries_qc.csv"
        )
      ),
      row.names = FALSE
    )

    # Report automatic VT together with fixed-t* sensitivity values.
    data.frame(
      analog_id = analog_id,
      cp_header = cols$cp,
      ct_header = paste0(
        cols$inter,
        " + ",
        cols$intra
      ),
      fit_window_min = max(
        t,
        na.rm = TRUE
      ),

      VT = auto$VT,
      tstar_min = auto$tstar,
      r2 = auto$r2,
      auto_note = auto$note,

      ct_eps = CT_EPS,
      ct_tail_fraction = CT_TAIL_FRACTION,
      ct_tail_eps = ct_tail_eps,

      vt_sensitivity_warn = vt_warn,

      VT_tstar10 = sens$VT[
        sens$tstar == 10
      ],
      VT_tstar15 = sens$VT[
        sens$tstar == 15
      ],
      VT_tstar20 = sens$VT[
        sens$tstar == 20
      ],
      VT_tstar25 = sens$VT[
        sens$tstar == 25
      ],
      VT_tstar30 = sens$VT[
        sens$tstar == 30
      ],
      VT_tstar35 = sens$VT[
        sens$tstar == 35
      ],
      VT_tstar40 = sens$VT[
        sens$tstar == 40
      ],

      error = "",
      row.names = NULL
    )
  }, error = function(e) {
    data.frame(
      analog_id = analog_id,
      cp_header = cols_used$cp,
      ct_header = if (
        nzchar(cols_used$inter) &&
          nzchar(cols_used$intra)
      ) {
        paste0(
          cols_used$inter,
          " + ",
          cols_used$intra
        )
      } else {
        ""
      },

      fit_window_min = FIT_WINDOW_MIN,

      VT = NA_real_,
      tstar_min = NA_real_,
      r2 = NA_real_,
      auto_note = "",

      ct_eps = CT_EPS,
      ct_tail_fraction = CT_TAIL_FRACTION,
      ct_tail_eps = NA_real_,

      vt_sensitivity_warn = NA,

      VT_tstar10 = NA_real_,
      VT_tstar15 = NA_real_,
      VT_tstar20 = NA_real_,
      VT_tstar25 = NA_real_,
      VT_tstar30 = NA_real_,
      VT_tstar35 = NA_real_,
      VT_tstar40 = NA_real_,

      error = conditionMessage(e),
      row.names = NULL
    )
  })

  write.csv(
    res_row,
    file.path(
      fits_dir,
      paste0(
        analog_id,
        "_logan_vt_results.csv"
      )
    ),
    row.names = FALSE
  )

  master_rows[[analog_id]] <- res_row
}

master <- do.call(
  rbind,
  master_rows
)

master_output <- file.path(
  output_dir,
  "MASTER_VT_logan_with_sensitivity.csv"
)

write.csv(
  master,
  master_output,
  row.names = FALSE
)

message("\nDone.")
message("MASTER: ", master_output)
message("Per-analog plots: ", figures_dir)
message("Per-analog sensitivity files: ", qc_dir)
message("Per-analog time-series QC files: ", qc_dir)
message("Per-analog fit results: ", fits_dir)
