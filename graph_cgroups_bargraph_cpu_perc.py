#!/usr/bin/env python3
import re
import os
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


############# CONFIGURATION ###############
policy_labels = ["EEVDF", "RR", "UFS"]

policy_colors = {
    "EEVDF": "#e6e6e6",
    "RR": "#d493b8",
    "UFS": "#9ccc65",
}

sched_configs = {
    "EEVDF": {
        "sched": "eevdf",
        "tracked_pids": [1175032, 1175033, 1175034, 1175035],
    },
    "RR": {
        "sched": "RR",
        "tracked_pids": [1219886, 1219887, 1219888, 1219889],
    },
    "UFS": {
        "sched": "ufs",
        "tracked_pids": [1167017, 1167018, 1167019, 1167020],
    },
}
###########################################

CPUSET = "0,2,4,6"
OUTPUT_FILE = "benchmark_runtime_histogram_all_sched_split_xaxis.pdf"

LINE_RE = re.compile(
    r"""
    \[
        (?P<cpu>\d+)
    \]
    .*?
    (?P<ts>\d+\.\d+):
    \s+
    (?P<event>sched_switch|sched_wakeup|sched_wakeup_new|sched_migrate_task):
    \s*
    (?P<rest>.*)
    $
    """,
    re.VERBOSE,
)

PREV_PID_RE = re.compile(r"\bprev_pid=(\d+)\b")
NEXT_PID_RE = re.compile(r"\bnext_pid=(\d+)\b")


def parse_cpuset(cpuset_text: str):
    cpus = set()
    text = cpuset_text.strip()
    if not text:
        return cpus

    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            cpus.update(range(start, end + 1))
        else:
            cpus.add(int(part))
    return cpus


def ts_to_ns(ts_str: str) -> int:
    sec_s, frac_s = ts_str.split(".", 1)
    frac_ns = (frac_s + "000000000")[:9]
    return int(sec_s) * 1_000_000_000 + int(frac_ns)


def compute_runtime_by_cpu(log_path: Path, allowed_cpus, tracked_pids):
    if not log_path.exists():
        raise FileNotFoundError(f"{log_path} not found")

    tracked_pids = set(tracked_pids)

    current_pid_by_cpu = {}
    current_start_ns_by_cpu = {}
    runtime_by_cpu = defaultdict(int)

    first_ts_ns = None
    last_ts_ns = None
    seen_cpus = set()

    with log_path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            m = LINE_RE.search(line)
            if not m:
                continue

            cpu = int(m.group("cpu"))
            if cpu not in allowed_cpus:
                continue

            event = m.group("event")
            ts_ns = ts_to_ns(m.group("ts"))
            rest = m.group("rest")

            seen_cpus.add(cpu)

            if first_ts_ns is None:
                first_ts_ns = ts_ns
            last_ts_ns = ts_ns

            if event != "sched_switch":
                continue

            prev_m = PREV_PID_RE.search(rest)
            next_m = NEXT_PID_RE.search(rest)
            if not prev_m or not next_m:
                continue

            next_pid = int(next_m.group(1))

            if cpu in current_pid_by_cpu:
                running_pid = current_pid_by_cpu[cpu]
                start_ns = current_start_ns_by_cpu[cpu]
                delta_ns = ts_ns - start_ns
                if delta_ns > 0 and running_pid in tracked_pids:
                    runtime_by_cpu[cpu] += delta_ns

            current_pid_by_cpu[cpu] = next_pid
            current_start_ns_by_cpu[cpu] = ts_ns

    if first_ts_ns is None or last_ts_ns is None:
        raise RuntimeError(f"No matching scheduler events found in {log_path} for cpuset {CPUSET}")

    for cpu, running_pid in current_pid_by_cpu.items():
        start_ns = current_start_ns_by_cpu[cpu]
        delta_ns = last_ts_ns - start_ns
        if delta_ns > 0 and running_pid in tracked_pids:
            runtime_by_cpu[cpu] += delta_ns

    return runtime_by_cpu, sorted(seen_cpus)


def plot_histogram(all_runtime_by_sched, cpus_sorted, output_path):
    intra_gap = 1.0
    cluster_gap = 1.6
    bar_width = 0.82

    fig, ax = plt.subplots(figsize=(11, 4.8))

    xtick_positions = []
    xtick_labels = []
    separator_positions = []
    global_max = 0.0
    legend_handles = []

    cluster_start = 0.0

    for policy_idx, policy in enumerate(policy_labels):
        runtime_by_cpu = all_runtime_by_sched[policy]
        cpu_totals = [runtime_by_cpu.get(cpu, 0) for cpu in cpus_sorted]

        max_total = max(cpu_totals, default=0)
        if max_total <= 0:
            max_total = 1

        normalized_values = [100.0 * total / max_total for total in cpu_totals]
        positions = [cluster_start + i * intra_gap for i in range(len(cpus_sorted))]

        bars = ax.bar(
            positions,
            normalized_values,
            bar_width,
            color=policy_colors[policy],
            edgecolor="black",
            linewidth=1.0,
            label=policy,
        )

        legend_handles.append(bars[0])

        xtick_positions.extend(positions)
        xtick_labels.extend([str(cpu) for cpu in cpus_sorted])

        global_max = max(global_max, max(normalized_values, default=0))

        last_pos = positions[-1]
        next_cluster_start = last_pos + intra_gap + cluster_gap
        if policy_idx < len(policy_labels) - 1:
            separator_positions.append((last_pos + next_cluster_start) / 2.0)

        cluster_start = next_cluster_start

    for sep_x in separator_positions:
        ax.axvline(sep_x, color="black", linewidth=1.0, alpha=0.45)

    ax.set_xticks(xtick_positions)
    ax.set_xticklabels(xtick_labels, fontsize=15)
    ax.set_xlabel("CPU ID", fontsize=18)
    ax.set_ylabel("Normalized Utilization\n(% of busiest CPU)", fontsize=18)

    ax.tick_params(axis="y", labelsize=15)
    ax.tick_params(axis="x", labelsize=15)

    ax.legend(
        legend_handles,
        policy_labels,
        fontsize=16,
        ncols=3,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.34),
        frameon=True,
        columnspacing=1.2,
        handletextpad=0.5,
    )

    ax.grid(axis="y", alpha=0.35)
    ax.set_ylim(0, max(106, global_max * 1.08))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")
    #os.system(f'brave "{output_path}"')
    plt.show()



allowed_cpus = parse_cpuset(CPUSET)
all_runtime_by_sched = {}
all_seen_cpus = set()

for policy in policy_labels:
    cfg = sched_configs[policy]
    sched = cfg["sched"]
    tracked_pids = cfg["tracked_pids"]
    log_file = Path(f"log/trace_tpcc_{sched}_4_4.log".lower())

    runtime_by_cpu, seen_cpus = compute_runtime_by_cpu(log_file, allowed_cpus, tracked_pids)
    all_runtime_by_sched[policy] = runtime_by_cpu
    all_seen_cpus.update(seen_cpus)

cpus_sorted = sorted(all_seen_cpus)
plot_histogram(all_runtime_by_sched, cpus_sorted, OUTPUT_FILE)
