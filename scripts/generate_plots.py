
import csv
import random
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
PLOTS_DIR = ROOT / "plots"

RAW_RESULTS = RESULTS_DIR / "raw_results.csv"
SUMMARY_CSV = RESULTS_DIR / "summary.csv"
SUMMARY_MD = RESULTS_DIR / "summary.md"

OPERATIONS = ("average", "variance")
THREAD_COUNTS = (1, 2, 3, 4)

# Bootstrap settings for uncertainty estimates.
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 42


def percentile(values, fraction):
    """Return a linearly interpolated percentile."""
    if not values:
        raise ValueError("Cannot calculate a percentile from empty data.")

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower

    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def load_results():
    measurements = defaultdict(list)

    with RAW_RESULTS.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required = {"operation", "threads", "repetition", "elapsed_seconds"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"CSV must contain these columns: {sorted(required)}"
            )

        for row in reader:
            operation = row["operation"]
            threads = int(row["threads"])
            elapsed = float(row["elapsed_seconds"])

            if operation not in OPERATIONS:
                raise ValueError(f"Unknown operation: {operation}")

            if threads not in THREAD_COUNTS:
                raise ValueError(f"Unexpected thread count: {threads}")

            if elapsed <= 0:
                raise ValueError(f"Invalid runtime: {elapsed}")

            measurements[(operation, threads)].append(elapsed)

    return measurements


def bootstrap_median(values, rng):
    """Estimate a median's confidence interval by resampling measurements."""
    estimates = []
    count = len(values)

    for _ in range(BOOTSTRAP_ITERATIONS):
        sample = [rng.choice(values) for _ in range(count)]
        estimates.append(statistics.median(sample))

    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def bootstrap_speedup(baseline, current, rng):
    """
    Bootstrap the speedup ratio:
        median(single-thread runtime) / median(current runtime)
    """
    estimates = []
    baseline_count = len(baseline)
    current_count = len(current)

    for _ in range(BOOTSTRAP_ITERATIONS):
        sampled_baseline = [
            rng.choice(baseline) for _ in range(baseline_count)
        ]
        sampled_current = [
            rng.choice(current) for _ in range(current_count)
        ]

        current_median = statistics.median(sampled_current)
        if current_median > 0:
            estimates.append(
                statistics.median(sampled_baseline) / current_median
            )

    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def calculate_summary(measurements):
    summary = []
    rng = random.Random(BOOTSTRAP_SEED)

    for operation in OPERATIONS:
        baseline_key = (operation, 1)

        if baseline_key not in measurements:
            raise ValueError(f"Missing baseline measurements for {operation}.")

        baseline = measurements[baseline_key]

        for threads in THREAD_COUNTS:
            key = (operation, threads)

            if key not in measurements or not measurements[key]:
                raise ValueError(
                    f"Missing measurements for {operation}, {threads} threads."
                )

            times = measurements[key]
            median_time = statistics.median(times)
            mean_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
            q1 = percentile(times, 0.25)
            q3 = percentile(times, 0.75)

            speedup = statistics.median(baseline) / median_time
            efficiency = speedup / threads

            median_ci_low, median_ci_high = bootstrap_median(times, rng)
            speedup_ci_low, speedup_ci_high = bootstrap_speedup(
                baseline, times, rng
            )

            summary.append({
                "operation": operation,
                "threads": threads,
                "runs": len(times),
                "median_seconds": median_time,
                "mean_seconds": mean_time,
                "std_dev_seconds": std_dev,
                "q1_seconds": q1,
                "q3_seconds": q3,
                "iqr_seconds": q3 - q1,
                "median_ci_low": median_ci_low,
                "median_ci_high": median_ci_high,
                "speedup": speedup,
                "speedup_ci_low": speedup_ci_low,
                "speedup_ci_high": speedup_ci_high,
                "efficiency": efficiency,
            })

    return summary


def save_summary_csv(summary):
    fieldnames = list(summary[0].keys())

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in summary:
            formatted = row.copy()

            for key, value in formatted.items():
                if key not in ("operation", "threads", "runs"):
                    formatted[key] = f"{value:.6f}"

            writer.writerow(formatted)


def save_summary_markdown(summary):
    lines = [
        "# Benchmark Summary",
        "",
        "Runtime is summarized using the median and interquartile range (IQR).",
        "IQR = 75th percentile - 25th percentile.",
        "Speedup = single-thread median / current median.",
        "Efficiency = speedup / thread count.",
        "Bootstrap confidence intervals use 10,000 resamples.",
        "The confidence intervals are estimates, not guarantees.",
        "",
        "| Operation | Threads | Runs | Median (s) | Q1 (s) | Q3 (s) | IQR (s) | Speedup | Speedup 95% CI | Efficiency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in summary:
        ci = (
            f"{row['speedup_ci_low']:.2f}–"
            f"{row['speedup_ci_high']:.2f}"
        )

        lines.append(
            f"| {row['operation']} "
            f"| {row['threads']} "
            f"| {row['runs']} "
            f"| {row['median_seconds']:.6f} "
            f"| {row['q1_seconds']:.6f} "
            f"| {row['q3_seconds']:.6f} "
            f"| {row['iqr_seconds']:.6f} "
            f"| {row['speedup']:.2f}x "
            f"| {ci} "
            f"| {row['efficiency']:.1%} |"
        )

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_rows(summary, operation):
    return sorted(
        (row for row in summary if row["operation"] == operation),
        key=lambda row: row["threads"],
    )


def plot_runtime(summary):
    fig, ax = plt.subplots(figsize=(8, 5))

    for operation in OPERATIONS:
        rows = get_rows(summary, operation)
        threads = [row["threads"] for row in rows]
        medians = [row["median_seconds"] for row in rows]

        lower_errors = [
            row["median_seconds"] - row["q1_seconds"] for row in rows
        ]
        upper_errors = [
            row["q3_seconds"] - row["median_seconds"] for row in rows
        ]

        ax.errorbar(
            threads,
            medians,
            yerr=[lower_errors, upper_errors],
            marker="o",
            capsize=4,
            label=operation.capitalize(),
        )

    ax.set(
        title="Runtime vs. Thread Count",
        xlabel="Number of threads",
        ylabel="Median runtime (seconds)",
        xticks=list(THREAD_COUNTS),
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "runtime.png", dpi=200)
    plt.close(fig)


def plot_speedup(summary):
    fig, ax = plt.subplots(figsize=(8, 5))

    for operation in OPERATIONS:
        rows = get_rows(summary, operation)
        threads = [row["threads"] for row in rows]
        speedups = [row["speedup"] for row in rows]

        ax.plot(threads, speedups, marker="o", label=operation.capitalize())

    ax.plot(
        THREAD_COUNTS,
        THREAD_COUNTS,
        linestyle="--",
        label="Ideal linear speedup",
    )

    ax.set(
        title="Parallel Speedup vs. Thread Count",
        xlabel="Number of threads",
        ylabel="Speedup (×)",
        xticks=list(THREAD_COUNTS),
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "speedup.png", dpi=200)
    plt.close(fig)


def plot_efficiency(summary):
    fig, ax = plt.subplots(figsize=(8, 5))

    for operation in OPERATIONS:
        rows = get_rows(summary, operation)
        threads = [row["threads"] for row in rows]
        efficiencies = [row["efficiency"] for row in rows]

        ax.plot(
            threads,
            efficiencies,
            marker="o",
            label=operation.capitalize(),
        )

    ax.axhline(1.0, linestyle="--", label="Ideal efficiency")

    ax.set(
    title="Parallel Efficiency vs. Thread Count",
    xlabel="Number of threads",
    ylabel="Parallel efficiency",
    xticks=list(THREAD_COUNTS),
)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "efficiency.png", dpi=200)
    plt.close(fig)


def plot_runtime_distribution(measurements):
    fig, ax = plt.subplots(figsize=(10, 6))

    labels = []
    values = []

    for operation in OPERATIONS:
        for threads in THREAD_COUNTS:
            key = (operation, threads)
            if key in measurements:
                labels.append(f"{operation}\n{threads} thread(s)")
                values.append(measurements[key])

    ax.boxplot(values, tick_labels=labels, showmeans=True)
    ax.set(
        title="Runtime Distribution Across Repeated Runs",
        xlabel="Operation and thread count",
        ylabel="Runtime (seconds)",
    )
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "runtime_distribution.png", dpi=200)
    plt.close(fig)


def plot_speedup_ci(summary):
    fig, ax = plt.subplots(figsize=(8, 5))

    for operation in OPERATIONS:
        rows = get_rows(summary, operation)
        threads = [row["threads"] for row in rows]
        speedups = [row["speedup"] for row in rows]

        lower_errors = [
            row["speedup"] - row["speedup_ci_low"] for row in rows
        ]
        upper_errors = [
            row["speedup_ci_high"] - row["speedup"] for row in rows
        ]

        ax.errorbar(
            threads,
            speedups,
            yerr=[lower_errors, upper_errors],
            marker="o",
            capsize=4,
            label=operation.capitalize(),
        )

    ax.plot(
        THREAD_COUNTS,
        THREAD_COUNTS,
        linestyle="--",
        label="Ideal linear speedup",
    )

    ax.set(
        title="Speedup with Bootstrap 95% Confidence Intervals",
        xlabel="Number of threads",
        ylabel="Speedup (×)",
        xticks=list(THREAD_COUNTS),
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "speedup_ci.png", dpi=200)
    plt.close(fig)


def main():
    if not RAW_RESULTS.exists():
        raise FileNotFoundError(
            f"Missing {RAW_RESULTS}. Run scripts/run_benchmarks.py first."
        )

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    measurements = load_results()
    summary = calculate_summary(measurements)

    save_summary_csv(summary)
    save_summary_markdown(summary)

    plot_runtime(summary)
    plot_speedup(summary)
    plot_efficiency(summary)
    plot_runtime_distribution(measurements)
    plot_speedup_ci(summary)

    print(f"Summary CSV: {SUMMARY_CSV}")
    print(f"Summary Markdown: {SUMMARY_MD}")
    print(f"Charts saved in: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
