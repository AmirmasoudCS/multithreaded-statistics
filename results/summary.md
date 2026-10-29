# Benchmark Summary

Runtime is summarized using the median and interquartile range (IQR).
IQR = 75th percentile - 25th percentile.
Speedup = single-thread median / current median.
Efficiency = speedup / thread count.
Bootstrap confidence intervals use 10,000 resamples.
The confidence intervals are estimates, not guarantees.

| Operation | Threads | Runs | Median (s) | Q1 (s) | Q3 (s) | IQR (s) | Speedup | Speedup 95% CI | Efficiency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| average | 1 | 20 | 0.031493 | 0.029922 | 0.031954 | 0.002033 | 1.00x | 0.95–1.05 | 100.0% |
| average | 2 | 20 | 0.017029 | 0.015032 | 0.017466 | 0.002434 | 1.85x | 1.76–2.01 | 92.5% |
| average | 3 | 20 | 0.014448 | 0.014173 | 0.014883 | 0.000710 | 2.18x | 2.07–2.23 | 72.7% |
| average | 4 | 20 | 0.014499 | 0.013454 | 0.015819 | 0.002365 | 2.17x | 1.98–2.33 | 54.3% |
| variance | 1 | 20 | 0.088592 | 0.084624 | 0.091394 | 0.006770 | 1.00x | 0.96–1.04 | 100.0% |
| variance | 2 | 20 | 0.048509 | 0.047785 | 0.049121 | 0.001336 | 1.83x | 1.76–1.89 | 91.3% |
| variance | 3 | 20 | 0.035706 | 0.035553 | 0.035903 | 0.000350 | 2.48x | 2.40–2.56 | 82.7% |
| variance | 4 | 20 | 0.031943 | 0.030857 | 0.035801 | 0.004944 | 2.77x | 2.52–2.88 | 69.3% |
