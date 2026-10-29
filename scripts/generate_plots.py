import csv
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


def load_results():
    measurements = defaultdict(list)

    with RAW_RESULTS.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required = {"operation", "threads", "elapsed_seconds"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                f"CSV must contain these columns: {sorted(required)}"
            )

        for row in reader:
            key = (row["operation"], int(row["threads"]))
            measurements[key].append(float(row["elapsed_seconds"]))

    return measurements


def calculate_summary(measurements):
    summary = []

    for operation in OPERATIONS:
        baseline_key = (operation, 1)

        if baseline_key not in measurements:
            raise ValueError(f"Missing baseline measurements for {operation}.")

        baseline = statistics.median(measurements[baseline_key])

        if baseline <= 0:
            raise ValueError(f"Invalid baseline runtime for {operation}.")

        for threads in THREAD_COUNTS:
            key = (operation, threads)

            if key not in measurements or not measurements[key]:
                raise ValueError(f"Missing measurements for {operation}, {threads} threads.")

            times = measurements[key]
            median_time = statistics.median(times)
            mean_time = statistics.mean(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0.0

            speedup = baseline / median_time
            efficiency = speedup / threads

            summary.append({
                "operation": operation,
                "threads": threads,
                "runs": len(times),
                "median_seconds": median_time,
                "mean_seconds": mean_time,
                "std_dev_seconds": std_dev,
                "speedup": speedup,
                "efficiency": efficiency,
            })

    return summary


def save_summary_csv(summary):
    fieldnames = [
        "operation",
        "threads",
        "runs",
        "median_seconds",
        "mean_seconds",
        "std_dev_seconds",
        "speedup",
        "efficiency",
    ]

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for row in summary:
            formatted = row.copy()
            for key in fieldnames:
                if key not in ("operation", "threads", "runs"):
                    formatted[key] = f"{row[key]:.6f}"
            writer.writerow(formatted)


def save_summary_markdown(summary):
    lines = [
        "# Benchmark Summary",
        "",
        "Runtime is reported as the median of repeated measurements.",
        "Speedup = single-thread median / current median.",
        "Efficiency = speedup / thread count.",
        "",
        "| Operation | Threads | Runs | Median (s) | Mean (s) | Std. dev. (s) | Speedup | Efficiency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for row in summary:
        lines.append(
            f"| {row['operation']} "
            f"| {row['threads']} "
            f"| {row['runs']} "
            f"| {row['median_seconds']:.6f} "
            f"| {row['mean_seconds']:.6f} "
            f"| {row['std_dev_seconds']:.6f} "
            f"| {row['speedup']:.2f}x "
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
        errors = [row["std_dev_seconds"] for row in rows]

        ax.errorbar(
            threads,
            medians,
            yerr=errors,
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

        ax.plot(threads, efficiencies, marker="o", label=operation.capitalize())

    ax.axhline(1.0, linestyle="--", label="Ideal efficiency")

    ax.set(
        title="Parallel Efficiency vs. Thread Count",
        xlabel="Number of threads",
        ylabel="Efficiency",
        xticks=list(THREAD_COUNTS),
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "efficiency.png", dpi=200)
    plt.close(fig)


def main():
    if not RAW_RESULTS.exists():
        raise FileNotFoundError(
            f"Missing {RAW_RESULTS}. Run scripts/run_benchmarks.py first."
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    measurements = load_results()
    summary = calculate_summary(measurements)

    save_summary_csv(summary)
    save_summary_markdown(summary)

    plot_runtime(summary)
    plot_speedup(summary)
    plot_efficiency(summary)

    print(f"Summary CSV: {SUMMARY_CSV}")
    print(f"Summary Markdown: {SUMMARY_MD}")
    print(f"Charts saved in: {PLOTS_DIR}")


if __name__ == "__main__":
    main()