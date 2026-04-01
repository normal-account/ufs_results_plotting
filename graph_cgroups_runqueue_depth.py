import re
import os
import matplotlib.pyplot as plt

############# CONFIGURATION ###############
TRACE_FILE = "log/trace_tpcc_eevdf_4_4.log"
TRACKED_PIDS = [1175032, 1175033, 1175034, 1175035]

CPUSET = [0, 2, 4, 6]
###########################################

############# WINDOW CONFIG ###############
SKIP_SECONDS = 16.0
DURATION_S = 1.0
###########################################

############# EXPORT CONFIG ###############
OUTPUT_PATH = "benchmark_runqueue_depth.pdf"
FIG_SIZE = (12, 6)
###########################################

############ PALETTE CONFIG ###############
CPU_COLORS = [
    "#0072B2",  # blue
    "#D55E00",  # red-orange-ish
    "#009E73",  # green
    "#CC79A7",  # pink-ish
]
###########################################


def parse_data(trace_file, TRACKED_PIDS, CPUSET):
    TRACKED_PIDS = set(TRACKED_PIDS)
    allowed_cpus = list(CPUSET)
    allowed_CPUSET = set(allowed_cpus)

    if not TRACKED_PIDS:
        raise ValueError("TRACKED_PIDS is empty.")
    if not allowed_cpus:
        raise ValueError("CPUSET is empty.")

    cpu_loads = {cpu: [] for cpu in allowed_cpus}
    runqueues = {cpu: set() for cpu in allowed_cpus}
    task_location = {}

    start_offset = None
    window_end = SKIP_SECONDS + DURATION_S

    ts_pat = re.compile(r"(\d+\.\d+):")
    cpu_pat = re.compile(r"\[(\d+)\]")
    sw_pat = re.compile(r"sched_switch:.*prev_pid=(\d+).*prev_state=(\S+).*next_pid=(\d+)")
    wu_pat = re.compile(r"sched_wakeup(?:_new)?:.*pid=(\d+).*target_cpu=(\d+)")
    mig_pat = re.compile(r"sched_migrate_task:.*pid=(\d+).*orig_cpu=(\d+).*dest_cpu=(\d+)")

    print(f"Parsing trace... Window: {SKIP_SECONDS}s to {window_end}s")
    print(f"Tracking CPUs: {allowed_cpus}")
    print(f"Tracking PIDs: {sorted(TRACKED_PIDS)}")

    with open(trace_file, "r") as f:
        for line in f:
            if "sched_" not in line:
                continue

            ts_m = ts_pat.search(line)
            if not ts_m:
                continue
            ts = float(ts_m.group(1))

            if start_offset is None:
                start_offset = ts

            rel_ts = ts - start_offset
            if rel_ts > window_end:
                break

            def record_load(cpu_id):
                if rel_ts < SKIP_SECONDS or cpu_id not in allowed_CPUSET:
                    return
                count = len(runqueues[cpu_id])
                if not cpu_loads[cpu_id] or cpu_loads[cpu_id][-1][1] != count:
                    cpu_loads[cpu_id].append((rel_ts, count))

            if "sched_switch" in line:
                cp_m = cpu_pat.search(line)
                sw_m = sw_pat.search(line)
                if not (cp_m and sw_m):
                    continue

                cpu = int(cp_m.group(1))
                prev_pid = int(sw_m.group(1))
                prev_state = sw_m.group(2)
                next_pid = int(sw_m.group(3))

                if next_pid in TRACKED_PIDS:
                    old_cpu = task_location.get(next_pid)
                    if old_cpu in allowed_CPUSET and old_cpu != cpu:
                        runqueues[old_cpu].discard(next_pid)
                        record_load(old_cpu)

                if cpu in allowed_CPUSET:
                    if prev_pid in TRACKED_PIDS:
                        if "R" in prev_state or "+" in prev_state:
                            runqueues[cpu].add(prev_pid)
                        else:
                            runqueues[cpu].discard(prev_pid)

                    if next_pid in TRACKED_PIDS:
                        runqueues[cpu].add(next_pid)

                    record_load(cpu)

                if next_pid in TRACKED_PIDS:
                    task_location[next_pid] = cpu
                if prev_pid in TRACKED_PIDS:
                    task_location[prev_pid] = cpu

            elif "sched_wakeup" in line:
                wu_m = wu_pat.search(line)
                if not wu_m:
                    continue

                pid = int(wu_m.group(1))
                target_cpu = int(wu_m.group(2))

                if pid not in TRACKED_PIDS:
                    continue

                old_cpu = task_location.get(pid)
                if old_cpu in allowed_CPUSET and old_cpu != target_cpu:
                    runqueues[old_cpu].discard(pid)
                    record_load(old_cpu)

                if target_cpu in allowed_CPUSET:
                    runqueues[target_cpu].add(pid)
                    record_load(target_cpu)

                task_location[pid] = target_cpu

            elif "sched_migrate_task" in line:
                mig_m = mig_pat.search(line)
                if not mig_m:
                    continue

                pid = int(mig_m.group(1))
                orig_cpu = int(mig_m.group(2))
                dest_cpu = int(mig_m.group(3))

                if pid not in TRACKED_PIDS:
                    continue

                if orig_cpu in allowed_CPUSET:
                    runqueues[orig_cpu].discard(pid)
                    record_load(orig_cpu)

                if dest_cpu in allowed_CPUSET:
                    runqueues[dest_cpu].add(pid)
                    record_load(dest_cpu)

                task_location[pid] = dest_cpu

    return cpu_loads


def plot_and_save(loads, CPUSET):
    fig, ax = plt.subplots(figsize=FIG_SIZE)

    fig.text(
        0.09, 0.5,
        "Runnable tasks per CPU",
        va="center",
        ha="center",
        rotation="vertical",
        fontsize=11,
        fontweight="bold",
    )
    
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.axisbelow"] = True

    window_end = SKIP_SECONDS + DURATION_S
    max_depth = len(TRACKED_PIDS)
    lane_gap = 0.8
    lane_span = max_depth + lane_gap

    for i, cpu in enumerate(CPUSET):
        data = loads.get(cpu, [])

        if data:
            times, values = zip(*data)
            times = list(times)
            values = list(values)

            if times[-1] < window_end:
                times.append(window_end)
                values.append(values[-1])

            if times[0] > SKIP_SECONDS:
                times.insert(0, SKIP_SECONDS)
                values.insert(0, values[0])
        else:
            times = [SKIP_SECONDS, window_end]
            values = [0, 0]

        norm_times = [t - SKIP_SECONDS for t in times]
        color = CPU_COLORS[i % len(CPU_COLORS)]

        base = i * lane_span
        top = [base + v for v in values]

        ax.fill_between(
            norm_times,
            base,
            top,
            step="post",
            color=color,
            alpha=1.0,
            linewidth=0,
        )

        ax.step(
            norm_times,
            top,
            where="post",
            color=color,
            linewidth=0.01,
        )

        # lane baseline
        ax.axhline(base, color="black", linewidth=0.7, alpha=0.5)

        # horizontal guides and numeric depth labels within each lane
        for d in range(1, max_depth + 1):
            y = base + d
            ax.axhline(y, color="black", linewidth=0.35, alpha=0.12)
            ax.text(
                -0.010,
                y,
                str(d),
                va="center",
                ha="right",
                fontsize=8,
                color="black",
                clip_on=False,
            )

        # CPU label centered on the lane
        ax.text(
            -0.040,
            base + max_depth / 2.0,
            f"CPU {cpu}",
            va="center",
            ha="right",
            fontsize=10,
            fontweight="bold",
            clip_on=False,
        )

        # threshold line for contention
        ax.axhline(base + 1, color="#C0392B", linestyle="--", linewidth=1.0, alpha=0.6)

    total_height = len(CPUSET) * lane_span - lane_gap
    ax.set_ylim(0, total_height)
    ax.set_xlim(0, DURATION_S)

    # no default y tick labels as we draw our own
    ax.set_yticks([])

    ax.set_xlabel("Time (s)", fontsize=10, fontweight="bold")
    ax.set_title("Per-CPU Runqueue Depth Over Time (EEVDF)", fontsize=11, fontweight="bold")
    ax.grid(True, axis="x", linestyle=":", alpha=0.6)

    plt.subplots_adjust(left=0.20)
    print(f"Saved: {OUTPUT_PATH}")
    plt.savefig(OUTPUT_PATH, bbox_inches="tight")
    
    #os.system(f'brave "{OUTPUT_PATH}"')
    plt.show()


loads = parse_data(TRACE_FILE, TRACKED_PIDS, CPUSET)
plot_and_save(loads, CPUSET)