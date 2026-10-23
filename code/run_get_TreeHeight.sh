set -euo pipefail
cd "$(dirname "$0")/.."
Rscript code/get_TreeHeight.R data/trees.csv