# pound_hill_analysis.R
# Purpose: How does mean plant species richness per quadrat vary among the
#          March, May and October cultivation treatments at Pound Hill?
# Run from the project root:  Rscript code/pound_hill_analysis.R
# Inputs (read only, never modified): data/pound_hill_data.csv, data/pound_hill_meta_data.csv
# Outputs: results/pound_hill_plot_richness.csv, results/pound_hill_plot_richness.pdf

data_file <- "data/pound_hill_data.csv"
meta_file <- "data/pound_hill_meta_data.csv"
out_csv   <- "results/pound_hill_plot_richness.csv"
out_pdf   <- "results/pound_hill_plot_richness.pdf"

# ---- 1. Import and inspect ----
for (f in c(data_file, meta_file)) {
  if (!file.exists(f)) stop("File not found: ", f, " (run from the project root)", call. = FALSE)
}
meta <- read.csv(meta_file, sep = ";", strip.white = TRUE, stringsAsFactors = FALSE)
print(meta)

# The metadata must justify treating blanks as zeros (do not assume this for other datasets)
if (!any(grepl("observed absence", unlist(meta), ignore.case = TRUE))) {
  stop("Metadata does not say blanks are observed zeros; re-download the supplied metadata file.",
       call. = FALSE)
}

# header = FALSE: the first 4 rows hold quadrat labels, not column names. Read everything as text.
raw <- read.csv(data_file, header = FALSE, colClasses = "character", stringsAsFactors = FALSE)
print(dim(raw))
print(head(raw[, 1:6]))
stopifnot(identical(raw[1:4, 1], c("Cultivation", "Block", "Plot", "Quadrat")))

# ---- 2. Split into quadrat labels and a counts matrix ----
cultivation <- unlist(raw[1, -1], use.names = FALSE)
block       <- unlist(raw[2, -1], use.names = FALSE)
plot_id     <- as.integer(unlist(raw[3, -1], use.names = FALSE))
quadrat     <- unlist(raw[4, -1], use.names = FALSE)
species     <- trimws(raw[-(1:4), 1])              # some names have trailing spaces
stopifnot(!anyNA(plot_id), !anyDuplicated(species))

counts <- as.matrix(raw[-(1:4), -1])
counts[trimws(counts) == ""] <- "0"                # blank = species looked for but not found = 0
counts <- suppressWarnings(matrix(as.numeric(counts), nrow = nrow(counts)))
stopifnot(!anyNA(counts), all(counts >= 0))        # numeric and non-negative

# ---- 3. Wide -> long (one row per species per quadrat) ----
n_sp <- length(species)
n_q  <- length(quadrat)
long <- data.frame(
  Cultivation = rep(cultivation, each = n_sp),
  Block       = rep(block,       each = n_sp),
  Plot        = rep(plot_id,     each = n_sp),
  Quadrat     = rep(quadrat,     each = n_sp),
  Species     = rep(species,     times = n_q),
  Count       = as.vector(counts),                 # column-major: one quadrat's species stay together
  stringsAsFactors = FALSE
)
stopifnot(nrow(long) == n_sp * n_q)

# ---- 4. Quadrat richness = number of species with Count > 0 (not total individuals) ----
# A quadrat is identified by Cultivation + Block + Plot + Quadrat together (Q1 alone is not unique).
long$Present <- as.integer(long$Count > 0)
quad_rich <- aggregate(Present ~ Cultivation + Block + Plot + Quadrat, data = long, FUN = sum)
names(quad_rich)[names(quad_rich) == "Present"] <- "Richness"
stopifnot(nrow(quad_rich) == n_q)

# ---- 5. Plot-level mean richness (quadrat first, then plot) ----
plot_rich <- aggregate(Richness ~ Cultivation + Block + Plot, data = quad_rich, FUN = mean)
names(plot_rich)[names(plot_rich) == "Richness"] <- "MeanRichness"
plot_rich <- plot_rich[order(plot_rich$Plot), c("Cultivation", "Block", "Plot", "MeanRichness")]
row.names(plot_rich) <- NULL
stopifnot(nrow(plot_rich) == 12, !anyDuplicated(plot_rich$Plot))
print(plot_rich)
cat("Distinct species:", length(unique(long$Species)),
    "| quadrats:", nrow(quad_rich),
    "| plots:", nrow(plot_rich), "\n")             # expect 41 | 59 | 12

dir.create("results", showWarnings = FALSE)
write.csv(plot_rich, out_csv, row.names = FALSE)    # overwrites on rerun

# ---- 6. Figure: each point is one plot; the line is the treatment mean ----
plot_rich$Cultivation <- factor(plot_rich$Cultivation,
                                levels = c("march", "may", "october"),
                                labels = c("March", "May", "October"))
set.seed(1)                                         # same jitter every run
pdf(out_pdf, width = 6, height = 5)
stripchart(MeanRichness ~ Cultivation, data = plot_rich,
           vertical = TRUE, method = "jitter", jitter = 0.08,
           pch = 19, col = "steelblue", las = 1,
           ylim = c(0, ceiling(max(plot_rich$MeanRichness)) + 2),
           xlab = "Cultivation month",
           ylab = "Mean species richness per quadrat (species)")
trt_mean <- tapply(plot_rich$MeanRichness, plot_rich$Cultivation, mean)
segments(x0 = 1:3 - 0.25, x1 = 1:3 + 0.25, y0 = trt_mean, lwd = 2)
legend("topright", legend = c("Plot (n = 4 per month)", "Treatment mean"),
       pch = c(19, NA), lty = c(NA, 1), lwd = c(NA, 2), col = c("steelblue", "black"), bty = "n")
invisible(dev.off())
message("Wrote ", out_csv, " and ", out_pdf)

# ---- 7. Interpretation  ----
# Interpretation
# The May cultivation treatment showed the highest mean species richness
# per quadrat (9.65 species), compared with March (7.81) and October (7.61).
# Plot-level richness varied within each treatment, and the observed values
# overlapped across the three cultivation months.
# These descriptive results do not establish a causal effect of cultivation
# timing; further analysis should consider block effects, environmental
# differences, and the limited number of replicate plots.