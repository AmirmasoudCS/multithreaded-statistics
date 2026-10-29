import argparse
import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXECUTABLE = ROOT / "src" / "benchmark.exe"
RESULTS_DIR = ROOT / "results"
RAW_RESULTS = RESULTS_DIR / "raw_results.csv"

OPERATIONS = ("average", "variance")
THREAD_COUNTS = (1, 2, 3, 4)


def run_once(operation, threads):
    """Run the C executable and parse its RESULT line."""
    process = subprocess.run(
        [str(EXECUTABLE), operation, str(threads)],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in process.stdout.splitlines():
        line = line.strip()

        if line.startswith("RESULT,"):
            fields = line.split(",")

            if len(fields) != 5:
                raise ValueError(f"Unexpected RESULT format: {line}")

            _, returned_operation, returned_threads, value, elapsed = fields

            if returned_operation != operation:
                raise ValueError(f"Unexpected operation: {returned_operation}")

            if int(returned_threads) != threads:
                raise ValueError(f"Unexpected thread count: {returned_threads}")

            return float(value), float(elapsed)

    raise ValueError(
        f"No RESULT line found for {operation} with {threads} threads.\n"
        f"Program output:\n{process.stdout}\n{process.stderr}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark the parallel statistics C program."
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=10,
        help="Number of measured runs per configuration (default: 10).",
    )
    args = parser.parse_args()

    if args.repetitions < 1:
        parser.error("--repetitions must be at least 1.")

    if not EXECUTABLE.exists():
        print(f"Executable not found: {EXECUTABLE}", file=sys.stderr)
        print("Compile src/benchmark.c first.", file=sys.stderr)
        return 1

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    configurations = [
        (operation, threads)
        for operation in OPERATIONS
        for threads in THREAD_COUNTS
    ]

    total_runs = len(configurations) * args.repetitions
    completed = 0
    rows = []

    print(f"Executable: {EXECUTABLE}")
    print(f"Measured runs: {total_runs}")
    print("Starting benchmarks...\n")

    try:
        for operation, threads in configurations:
            print(f"Warm-up: {operation}, {threads} thread(s)")
            run_once(operation, threads)

            for repetition in range(1, args.repetitions + 1):
                value, elapsed = run_once(operation, threads)

                rows.append({
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                    "operation": operation,
                    "threads": threads,
                    "repetition": repetition,
                    "value": f"{value:.12f}",
                    "elapsed_seconds": f"{elapsed:.9f}",
                })

                completed += 1
                print(
                    f"[{completed}/{total_runs}] "
                    f"{operation:8s} | threads={threads} | "
                    f"run={repetition:02d} | "
                    f"value={value:.6f} | time={elapsed:.6f}s"
                )

    except (subprocess.CalledProcessError, ValueError, OSError) as error:
        print(f"\nBenchmark failed: {error}", file=sys.stderr)
        return 1

    fieldnames = [
        "timestamp",
        "operation",
        "threads",
        "repetition",
        "value",
        "elapsed_seconds",
    ]

    with RAW_RESULTS.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nCompleted successfully: {len(rows)} measurements")
    print(f"Raw results saved to: {RAW_RESULTS}")
    print("Next, run: python scripts/generate_plots.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())