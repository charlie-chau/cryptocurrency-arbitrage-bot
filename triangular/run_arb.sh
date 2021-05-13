#!/bin/sh

while true
do
  if [ ! -d "results_triangular/$(date +%Y%m%d)" ]; then
    mkdir results_triangular/$(date +%Y%m%d)
  fi
  python arb_finder_1.0.py > results_triangular/$(date +%Y%m%d)/arb_run_$(date +%Y-%m-%d_%H%M%S).txt
done
