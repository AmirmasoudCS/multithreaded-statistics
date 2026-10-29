# Benchmark Summary

Runtime is reported as the median of repeated measurements.
Speedup = single-thread median / current median.
Efficiency = speedup / thread count.

| Operation | Threads | Runs | Median (s) | Mean (s) | Std. dev. (s) | Speedup | Efficiency |
|---|---:|---:|---:|---:|---:|---:|---:|
| average | 1 | 10 | 0.032120 | 0.031320 | 0.001519 | 1.00x | 100.0% |
| average | 2 | 10 | 0.017445 | 0.017470 | 0.000292 | 1.84x | 92.1% |
| average | 3 | 10 | 0.013285 | 0.015192 | 0.003156 | 2.42x | 80.6% |
| average | 4 | 10 | 0.012529 | 0.013387 | 0.002047 | 2.56x | 64.1% |
| variance | 1 | 10 | 0.078040 | 0.081509 | 0.013769 | 1.00x | 100.0% |
| variance | 2 | 10 | 0.044973 | 0.045103 | 0.001879 | 1.74x | 86.8% |
| variance | 3 | 10 | 0.033209 | 0.035255 | 0.004356 | 2.35x | 78.3% |
| variance | 4 | 10 | 0.032373 | 0.033006 | 0.004497 | 2.41x | 60.3% |
