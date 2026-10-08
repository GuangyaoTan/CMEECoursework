#!/bin/bash
# Author: Your name you.login@imperial.ac.uk
# Script: tabtocsv.sh
# Desc: substitute the tabs in the files with commas
#       saves the output into a .csv file
# Arguments: 1-> tab delimited file
# Date: Oct 2015
if [ ! -f "$1" ]; then
    echo "Error: input file not found" >&2
    exit 1
fi
echo "Creating a comma delimited version of $1 ..."

output="../results/$(basename "$1").csv"

cat "$1" | tr '\t' ',' > "$output"

echo "Done!"

exit
