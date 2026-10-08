#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Error: please provide exactly one input file" >&2
    exit 1
fi

if [ ! -f "$1" ] || [ ! -r "$1" ]; then
    echo "Error: invalid or unreadable input file" >&2
    exit 1
fi

mkdir -p ../results

output="../results/$(basename "$1").txt"

if tr ',' ' ' < "$1" > "$output"; then
    echo "Done!"
else
    echo "Error: conversion failed" >&2
    exit 1
fi