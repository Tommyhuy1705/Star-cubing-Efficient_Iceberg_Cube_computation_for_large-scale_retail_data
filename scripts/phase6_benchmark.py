"""Phase 6 benchmark runner: Star-cubing vs BUC vs Bottom-up."""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence

import pandas as pd
import psutil

# Ensure imports work when the script is run from repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.algorithm import (  # noqa: E402
    FactRow,
    compute_bottom_up_cube,
    compute_buc_cube,
)
from src.algorithm.star_tree import StarTree  # noqa: E402

try:
    import matplotlib.pyplot as plt
except Exception as exc:  # pragma: no cover - explicit runtime check
    raise RuntimeError(
        "matplotlib is required to render benchmark charts. "
        "Install dependencies with: pip install -r requirements.txt"
    ) from exc

DIMENSION_NAMES: Sequence[str] = (
    "Time_Period",
    "Region",
    "City",
    "Category",
    "Customer_Type",
    "Payment_Method",
)


def generate_synthetic_rows(num_rows: int, seed: int) -> List[FactRow]:
    """Generate integer-encoded retail rows following the project contract."""

    rng = random.Random(seed)

    months = [202601, 202602, 202603, 202604]
    regions = [0, 1, 2]  # 0: North, 1: Central, 2: South
    city_by_region = {
        0: [0, 1, 2],
        1: [3, 4],
        2: [5, 6, 7],
    }
    categories = [0, 1, 2, 3]  # 0: Electronics
    payment_methods = [0, 1, 2]

    rows: List[FactRow] = []

    for _ in range(num_rows):
        month = rng.choice(months)
        region = rng.choice(regions)
        city = rng.choice(city_by_region[region])

        customer_type = 1 if rng.random() < 0.22 else 0  # 1: VIP, 0: Normal
        if customer_type == 1 and rng.random() < 0.8:
            category = 0
        else:
            category = rng.choice(categories)

        payment_method = rng.choice(payment_methods)
        quantity = rng.randint(1, 5)

        base = 180_000.0 + (category * 55_000.0) + (payment_method * 15_000.0)
        vip_multiplier = 1.35 if customer_type == 1 else 1.0
        sales = (base * quantity * vip_multiplier) + rng.uniform(5_000.0, 40_000.0)

        rows.append(
            FactRow(
                dimensions=(month, region, city, category, customer_type, payment_method),
                sales=float(round(sales, 2)),
                count_txn=1,
            )
        )

    return rows


def serialize_cube_size_bytes(cube_rows: Iterable[Dict[str, object]]) -> int:
    """Estimate serialized cube storage size as CSV bytes."""

    fieldnames = [*DIMENSION_NAMES, "total_sales", "count_txn"]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in cube_rows:
        writer.writerow(row)
    return len(output.getvalue().encode("utf-8"))


def benchmark_algorithm(
    name: str,
    compute_fn: Callable[[Iterable[FactRow], Sequence[str], float], List[Dict[str, object]]],
    rows: List[FactRow],
    min_sup: float,
) -> Dict[str, float]:
    """Run one benchmark pass and return timing/memory metrics."""

    process = psutil.Process()
    rss_before_mb = process.memory_info().rss / (1024 * 1024)
    cpu_before = time.process_time()
    start = time.perf_counter()

    tracemalloc.start()
    cube_rows = compute_fn(rows, DIMENSION_NAMES, min_sup)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_sec = time.perf_counter() - start
    cpu_sec = time.process_time() - cpu_before
    rss_after_mb = process.memory_info().rss / (1024 * 1024)

    storage_bytes = serialize_cube_size_bytes(cube_rows)
    cpu_utilization_pct = 0.0 if elapsed_sec == 0 else (cpu_sec / elapsed_sec) * 100.0

    return {
        "algorithm": name,
        "elapsed_sec": round(elapsed_sec, 6),
        "cpu_sec": round(cpu_sec, 6),
        "cpu_utilization_pct": round(cpu_utilization_pct, 3),
        "rss_before_mb": round(rss_before_mb, 3),
        "rss_after_mb": round(rss_after_mb, 3),
        "rss_delta_mb": round(rss_after_mb - rss_before_mb, 3),
        "tracemalloc_peak_mb": round(peak_bytes / (1024 * 1024), 3),
        "cube_rows": len(cube_rows),
        "output_storage_kb": round(storage_bytes / 1024.0, 3),
    }


def compute_star_tree_cube(
    rows: Iterable[FactRow],
    dimension_names: Sequence[str],
    min_sup: float,
) -> List[Dict[str, object]]:
    """Run StarTree aggregation directly for benchmark comparability."""

    tree = StarTree(dimension_names=dimension_names, min_sup=min_sup)
    for row in rows:
        tree.insert_transaction(
            transaction=list(row.dimensions),
            sales=float(row.sales),
            count=int(row.count_txn),
        )
    return tree.simultaneous_aggregation()


def build_charts(df: pd.DataFrame, chart_dir: Path) -> None:
    """Render runtime, memory, and storage comparison charts."""

    chart_dir.mkdir(parents=True, exist_ok=True)

    mean_runtime = (
        df.groupby(["algorithm", "dataset_rows"], as_index=False)["elapsed_sec"].mean()
    )
    plt.figure(figsize=(10, 6))
    for algo, frame in mean_runtime.groupby("algorithm"):
        frame = frame.sort_values("dataset_rows")
        plt.plot(frame["dataset_rows"], frame["elapsed_sec"], marker="o", label=algo)
    plt.title("Runtime Comparison by Dataset Size")
    plt.xlabel("Number of input rows")
    plt.ylabel("Elapsed time (seconds)")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_dir / "runtime_line.png", dpi=160)
    plt.close()

    mean_memory = (
        df.groupby("algorithm", as_index=False)["tracemalloc_peak_mb"].mean()
        .sort_values("tracemalloc_peak_mb")
    )
    plt.figure(figsize=(9, 6))
    plt.bar(mean_memory["algorithm"], mean_memory["tracemalloc_peak_mb"], width=0.6)
    plt.title("Average Python Heap Peak (tracemalloc)")
    plt.xlabel("Algorithm")
    plt.ylabel("Peak memory (MB)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(chart_dir / "memory_bar.png", dpi=160)
    plt.close()

    mean_storage = (
        df.groupby(["algorithm", "dataset_rows"], as_index=False)["output_storage_kb"].mean()
    )
    plt.figure(figsize=(10, 6))
    for algo, frame in mean_storage.groupby("algorithm"):
        frame = frame.sort_values("dataset_rows")
        plt.plot(frame["dataset_rows"], frame["output_storage_kb"], marker="s", label=algo)
    plt.title("Cube Output Storage by Dataset Size")
    plt.xlabel("Number of input rows")
    plt.ylabel("Serialized output size (KB)")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(chart_dir / "storage_line.png", dpi=160)
    plt.close()


def parse_sizes(sizes_raw: str) -> List[int]:
    """Parse comma-separated sizes from CLI argument."""

    sizes = [int(chunk.strip()) for chunk in sizes_raw.split(",") if chunk.strip()]
    if not sizes:
        raise ValueError("At least one dataset size must be provided")
    return sizes


def main() -> None:
    """CLI entry-point for Phase 6 benchmark workflow."""

    parser = argparse.ArgumentParser(description="Run Phase 6 benchmark suite")
    parser.add_argument(
        "--sizes",
        default="2000,5000,10000",
        help="Comma-separated list of row counts (default: 2000,5000,10000)",
    )
    parser.add_argument("--repeats", type=int, default=2, help="Runs per dataset size")
    parser.add_argument(
        "--min-sup",
        type=float,
        default=18_000_000.0,
        help="Iceberg threshold over Total_Sales",
    )
    parser.add_argument("--seed", type=int, default=20260418, help="Random seed")
    args = parser.parse_args()

    sizes = parse_sizes(args.sizes)
    base_dir = REPO_ROOT / "docs" / "phase6"
    log_dir = base_dir / "logs"
    chart_dir = base_dir / "charts"
    log_dir.mkdir(parents=True, exist_ok=True)

    algorithms: Dict[str, Callable[[Iterable[FactRow], Sequence[str], float], List[Dict[str, object]]]] = {
        "Star-cubing": compute_star_tree_cube,
        "BUC": compute_buc_cube,
        "Bottom-up": compute_bottom_up_cube,
    }

    records: List[Dict[str, object]] = []
    run_counter = 0

    for size in sizes:
        for repeat_idx in range(args.repeats):
            run_seed = args.seed + (size * 31) + repeat_idx
            rows = generate_synthetic_rows(num_rows=size, seed=run_seed)

            for algorithm_name, compute_fn in algorithms.items():
                run_counter += 1
                metrics = benchmark_algorithm(
                    name=algorithm_name,
                    compute_fn=compute_fn,
                    rows=rows,
                    min_sup=args.min_sup,
                )
                metrics.update(
                    {
                        "run_id": run_counter,
                        "repeat": repeat_idx + 1,
                        "dataset_rows": size,
                        "seed": run_seed,
                        "min_sup": args.min_sup,
                    }
                )
                records.append(metrics)
                print(
                    f"[{run_counter:02d}] {algorithm_name:<10} rows={size:<6} "
                    f"elapsed={metrics['elapsed_sec']:.4f}s "
                    f"peak={metrics['tracemalloc_peak_mb']:.3f}MB"
                )

    df = pd.DataFrame(records)
    csv_path = log_dir / "performance_log.csv"
    json_path = log_dir / "performance_log.json"
    summary_path = log_dir / "summary_by_algorithm.csv"

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=2)

    summary_df = (
        df.groupby("algorithm", as_index=False)
        .agg(
            elapsed_sec_mean=("elapsed_sec", "mean"),
            cpu_sec_mean=("cpu_sec", "mean"),
            tracemalloc_peak_mb_mean=("tracemalloc_peak_mb", "mean"),
            output_storage_kb_mean=("output_storage_kb", "mean"),
            cube_rows_mean=("cube_rows", "mean"),
        )
        .sort_values("elapsed_sec_mean")
    )
    summary_df.to_csv(summary_path, index=False)

    build_charts(df=df, chart_dir=chart_dir)

    print("\nBenchmark completed.")
    print(f"Log CSV: {csv_path}")
    print(f"Log JSON: {json_path}")
    print(f"Summary : {summary_path}")
    print(f"Charts  : {chart_dir}")


if __name__ == "__main__":
    main()
