required_cols <- c("Species", "Distance.m", "Angle.degrees")
usage <- "Usage: Rscript code/get_TreeHeight.R <path/to/file.csv>"

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) stop("Missing argument. ", usage, call. = FALSE)
if (length(args) > 1)  stop("Too many arguments (expected exactly 1). ", usage, call. = FALSE)

input_file <- args[1]
if (!file.exists(input_file)) stop("File not found: ", input_file, call. = FALSE)

trees <- read.csv(input_file, stringsAsFactors = FALSE)
if (!identical(names(trees), required_cols)) {
  stop("Header must be exactly: ", paste(required_cols, collapse = ","), call. = FALSE)
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

trees$height_m <- trees$Distance.m * tan(trees$Angle.degrees * pi / 180)

base_name   <- tools::file_path_sans_ext(basename(input_file))
output_file <- file.path("results", paste0(base_name, "_treeheights.csv"))
dir.create("results", showWarnings = FALSE)
write.csv(trees, output_file, row.names = FALSE)
message("Wrote ", nrow(trees), " rows to ", output_file)