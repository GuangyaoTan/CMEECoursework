input_file    <- "data/trees.csv"
output_file   <- "results/TreeHts.csv"
required_cols <- c("Species", "Distance.m", "Angle.degrees")

if (!file.exists(input_file)) stop("Input file not found: ", input_file, call. = FALSE)
trees <- read.csv(input_file, stringsAsFactors = FALSE)

missing_cols <- setdiff(required_cols, names(trees))
if (length(missing_cols) > 0) {
  stop("Missing required column(s): ", paste(missing_cols, collapse = ", "), call. = FALSE)
}

for (col in c("Distance.m", "Angle.degrees")) {
  if (!is.numeric(trees[[col]])) stop(col, " must be numeric", call. = FALSE)
  if (!all(is.finite(trees[[col]]))) stop(col, " contains NA/NaN/Inf", call. = FALSE)
}

if (any(trees$Distance.m <= 0 | trees$Distance.m > 100)) {
  stop("Distance.m must satisfy 0 < d <= 100", call. = FALSE)
}
if (any(trees$Angle.degrees <= 0 | trees$Angle.degrees >= 90)) {
  stop("Angle.degrees must satisfy 0 < angle < 90", call. = FALSE)
}

#Calculate tree height in meters using the formula: height = distance * tan(angle)
trees$height_m <- trees$Distance.m * tan(trees$Angle.degrees * pi / 180)

dir.create("results", showWarnings = FALSE)
write.csv(trees, output_file, row.names = FALSE)
message("Wrote ", nrow(trees), " rows to ", output_file)