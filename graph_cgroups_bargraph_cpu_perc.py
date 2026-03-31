#!/usr/bin/env python3
import re
import os
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Uncomment one of the 2 configs below, depending on the scheduler to plot
###################################################
### EEVDF config
SCHED = "eevdf"
TRACKED_PIDS = [1158657, 1158658, 1158659, 1158660]

### UFS config
# SCHED = "ufs"
# TRACKED_PIDS = [1167017, 1167018, 1167019, 1167020]
###################################################

LOG_FILE = f"trace_tpcc_{SCHED}_4_4.log"
OUTPUT_FILE = f"benchmark_runtime_histogram_{SCHED}.pdf"
CPUSET = "0,2,4,6"

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


def plot_histogram(runtime_by_cpu, cpus_sorted, output_path):
    cpu_totals = [runtime_by_cpu[cpu] for cpu in cpus_sorted]
    max_total = max(cpu_totals, default=0)
    if max_total <= 0:
        max_total = 1

    normalized_values = [100.0 * total / max_total for total in cpu_totals]

    x = cpus_sorted

    plt.figure(figsize=(12, 6))
    plt.bar(x, normalized_values, color="#808080", edgecolor="#4d4d4d", width=0.8)

    for cpu, value in zip(x, normalized_values):
        if value > 0:
            plt.text(cpu, value + 1.0, f"{value:.1f}%", ha="center", va="bottom", fontsize=9)

    plt.xticks(cpus_sorted)
    plt.xlabel("CPU")
    plt.ylabel("Normalized runtime (% of busiest CPU)")
    plt.title(f"TPC-C Runtime per CPU ({SCHED.upper()})")
    plt.ylim(0, max(105, max(normalized_values, default=0) * 1.08))
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Saved: {output_path}")
    os.system(f"brave \"{output_path}\"")


allowed_cpus = parse_cpuset(CPUSET)
tracked_pids = set(TRACKED_PIDS)

log_path = Path(LOG_FILE)
if not log_path.exists():
    raise FileNotFoundError(f"{LOG_FILE} not found")

# Per-CPU state: which task is currently running, and since when
current_pid_by_cpu = {}
current_start_ns_by_cpu = {}

# Aggregated tracked runtime per CPU
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

        # Account for the task that had been running on this CPU
        if cpu in current_pid_by_cpu:
            running_pid = current_pid_by_cpu[cpu]
            start_ns = current_start_ns_by_cpu[cpu]
            delta_ns = ts_ns - start_ns
            if delta_ns > 0 and running_pid in tracked_pids:
                runtime_by_cpu[cpu] += delta_ns

        # After the switch, next_pid starts running
        current_pid_by_cpu[cpu] = next_pid
        current_start_ns_by_cpu[cpu] = ts_ns

if first_ts_ns is None or last_ts_ns is None:
    raise RuntimeError("No matching scheduler events found in trace.log for the hardcoded cpuset")

# Flush the final running slice on each CPU up to the end of the observed window
for cpu, running_pid in current_pid_by_cpu.items():
    start_ns = current_start_ns_by_cpu[cpu]
    delta_ns = last_ts_ns - start_ns
    if delta_ns > 0 and running_pid in tracked_pids:
        runtime_by_cpu[cpu] += delta_ns

cpus_sorted = sorted(seen_cpus)
plot_histogram(runtime_by_cpu, cpus_sorted, OUTPUT_FILE)

