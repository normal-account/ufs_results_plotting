import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


############# CONFIGURATION ###############
benchmark = "IWL"
udf_label = "BWL"

clients = "8"


policy_labels = ["EEVDF", "IDLE", "FIFO", "RR", "UFS"]
policy_colors = {
    "EEVDF": "#f7f7f7",
    "IDLE": "#d9d9d9",
    "FIFO": "#e9a3c9",
    "RR": "#c51b7d",
    "UFS": "#b8e186",
}


###########################################


########### TEMPLATE CONFIG ###############

# UNCOMMENT THE BELOW CONFIGURATIONS DEPENDING ON THE EXPERIMENT TO PLOT.

### CONFIGURATION 1
### TPC-C EXPERIMENT: PERFORMANCE OF THE SCHEDULERS UNDER DIFFERENT SETTINGS
# groups = {
#     "filename": "plot_solo_vs_mixed.pdf",
#     "mixes": {
#         "SOLO": {
#             "EEVDF":        "results/client_8_0_tpcc_eevdf.csv",
#             "IDLE":         "results/client_8_0_tpcc_eevdf.csv",
#             "RR":           "results/client_8_0_tpcc_rr.csv",
#             "FIFO":         "results/client_8_0_tpcc_ff.csv",
#             "UFS":          "results/client_8_0_tpcc_ufs.csv"
#         },
#         "MIN:MAX": {
#             "EEVDF":        "results/client_8_8_tpcc_eevdf.csv",
#             "IDLE":         "results/client_8_8_tpcc_idle.csv",
#             "RR":           "results/client_8_8_tpcc_rr.csv",
#             "FIFO":         "results/client_8_8_tpcc_ff.csv",
#             "UFS":          "results/client_8_8_tpcc_ufs.csv"
#         },
#         "50:50 MIX": {
#             "EEVDF":        "results/client_8_8_tpcc_eevdf_same_prio.csv",
#             "IDLE":         "results/client_8_8_tpcc_idle_same_prio.csv",
#             "RR":           "results/client_8_8_tpcc_rr_same_prio.csv",
#             "FIFO":         "results/client_8_8_tpcc_ff_same_prio.csv",
#             "UFS":          "results/client_8_8_tpcc_ufs_same_prio.csv"
#         }
#     }
# }

# udf_groups = {
#     "SOLO": {
#         "EEVDF":        "results/udf_0_8_eevdf.csv",
#         "IDLE":         "results/udf_0_8_idle.csv",
#         "RR":           "results/udf_0_8_rr.csv",
#         "FIFO":         "results/udf_0_8_ff.csv",
#         "UFS":          "results/udf_0_8_ufs.csv"
#     },
#     "MIN:MAX": {
#         "EEVDF":        "results/udf_8_8_eevdf.csv",
#         "IDLE":         "results/udf_8_8_idle.csv",
#         "RR":           "results/udf_8_8_rr.csv",
#         "FIFO":         "results/udf_8_8_ff.csv",
#         "UFS":          "results/udf_8_8_ufs.csv"
#     },
#     "50:50 MIX": {
#         "EEVDF":        "results/udf_8_8_eevdf_same_prio.csv",
#         "IDLE":         "results/udf_8_8_idle_same_prio.csv",
#         "RR":           "results/udf_8_8_rr_same_prio.csv",
#         "FIFO":         "results/udf_8_8_ff_same_prio.csv",
#         "UFS":          "results/udf_8_8_ufs_same_prio.csv"
#     }
# }


### CONFIGURATION 1 BUT WITH SCHEDULER-HINTING
### TPC-C EXPERIMENT: PERFORMANCE OF THE SCHEDULERS UNDER DIFFERENT SETTINGS
# groups = {
#     "filename": "plot_solo_vs_mixed_with_hinting.pdf",
#     "mixes": {
#         "SOLO": {
#             "EEVDF":        "results_overhead/client_8_0_tpcc_eevdf.csv",
#             "IDLE":         "results_overhead/client_8_0_tpcc_eevdf.csv",
#             "RR":           "results_overhead/client_8_0_tpcc_rr.csv",
#             "FIFO":         "results_overhead/client_8_0_tpcc_ff.csv",
#             "UFS":          "results_overhead/client_8_0_tpcc_ufs.csv"
#         },
#         "MIN:MAX": {
#             "EEVDF":        "results_overhead/client_8_8_tpcc_eevdf.csv",
#             "IDLE":         "results_overhead/client_8_8_tpcc_idle.csv",
#             "RR":           "results_overhead/client_8_8_tpcc_rr.csv",
#             "FIFO":         "results_overhead/client_8_8_tpcc_ff.csv",
#             "UFS":          "results_overhead/client_8_8_tpcc_ufs.csv"
#         },
#         "50:50 MIX": {
#             "EEVDF":        "results_overhead/client_8_8_tpcc_eevdf_same_prio.csv",
#             "IDLE":         "results_overhead/client_8_8_tpcc_idle_same_prio.csv",
#             "RR":           "results_overhead/client_8_8_tpcc_rr_same_prio.csv",
#             "FIFO":         "results_overhead/client_8_8_tpcc_ff_same_prio.csv",
#             "UFS":          "results_overhead/client_8_8_tpcc_ufs_same_prio.csv"
#         }
#     }
# }

# udf_groups = {
#     "SOLO": {
#         "EEVDF":        "results_overhead/udf_0_8_eevdf.csv",
#         "IDLE":         "results_overhead/udf_0_8_idle.csv",
#         "RR":           "results_overhead/udf_0_8_rr.csv",
#         "FIFO":         "results_overhead/udf_0_8_ff.csv",
#         "UFS":          "results_overhead/udf_0_8_ufs.csv"
#     },
#     "MIN:MAX": {
#         "EEVDF":        "results_overhead/udf_8_8_eevdf.csv",
#         "IDLE":         "results_overhead/udf_8_8_idle.csv",
#         "RR":           "results_overhead/udf_8_8_rr.csv",
#         "FIFO":         "results_overhead/udf_8_8_ff.csv",
#         "UFS":          "results_overhead/udf_8_8_ufs.csv"
#     },
#     "50:50 MIX": {
#         "EEVDF":        "results_overhead/udf_8_8_eevdf_same_prio.csv",
#         "IDLE":         "results_overhead/udf_8_8_idle_same_prio.csv",
#         "RR":           "results_overhead/udf_8_8_rr_same_prio.csv",
#         "FIFO":         "results_overhead/udf_8_8_ff_same_prio.csv",
#         "UFS":          "results_overhead/udf_8_8_ufs_same_prio.csv"
#     }
# }

### CONFIGURATION 2
### TPC-C EXPERIMENT: THROUGHPUT W.R.T. NUMBER OF CLIENTS (OVERSUBSCRIPTION)
# groups = {
#     "filename": "plot_tpcc_oversubscription.pdf",
#     "mixes": {
#         "8B/8I": {
#             "EEVDF": "results/client_8_8_tpcc_eevdf.csv",
#             "RR":    "results/client_8_8_tpcc_rr.csv",
#             "UFS":   "results/client_8_8_tpcc_ufs.csv"
#         },
#         "8B/16I": {
#             "EEVDF": "results/client_16_8_tpcc_eevdf.csv",
#             "RR":    "results/client_16_8_tpcc_rr.csv",
#             "UFS":   "results/client_16_8_tpcc_ufs.csv"
#         },
#         "8B/24I": {
#             "EEVDF": "results/client_24_8_tpcc_eevdf.csv",
#             "RR":    "results/client_24_8_tpcc_rr.csv",
#             "UFS":   "results/client_24_8_tpcc_ufs.csv"
#         },
#         # "32 TPC-C vs 8 UDFs": {
#         #     "EEVDF": "results/client_32_8_tpcc_eevdf.csv",
#         #     "RR":    "results/client_32_8_tpcc_rr.csv",
#         #     "UFS":   "results/client_32_8_tpcc_ufs.csv"
#         # }
#     }
# }

# udf_groups = {

# }


### CONFIGURATION 3
### YCSB EXPERIMENT: THROUGHPUT W.R.T NUMBER OF CLIENTS (OVERSUBSCRIPTION)
# benchmark = "YCSB"
# groups = {
#     "filename": "plot_ycsb_oversubscription.pdf",
#     "mixes": {
#         "Baseline (8 YCSB vs 8 UDFs)": {
#             "EEVDF": "results/client_8_8_ycsb_eevdf.csv",
#             "RR":    "results/client_8_8_ycsb_rr.csv",
#             "UFS":   "results/client_8_8_ycsb_ufs.csv"
#         },
#         "16 YCSB vs 8 UDFs": {
#             "EEVDF": "results/client_16_8_ycsb_eevdf.csv",
#             "RR":    "results/client_16_8_ycsb_rr.csv",
#             "UFS":   "results/client_16_8_ycsb_ufs.csv"
#         },
#         "24 YCSB vs 8 UDFs": {
#             "EEVDF": "results/client_24_8_ycsb_eevdf.csv",
#             "RR":    "results/client_24_8_ycsb_rr.csv",
#             "UFS":   "results/client_24_8_ycsb_ufs.csv"
#         },
#         "32 YCSB vs 8 UDFs": {
#             "EEVDF": "results/client_32_8_ycsb_eevdf.csv",
#             "RR":    "results/client_32_8_ycsb_rr.csv",
#             "UFS":   "results/client_32_8_ycsb_ufs.csv"
#         }
#     }
# }
#
# udf_groups = {
#     "Baseline (8 YCSB vs 8 UDFs)": {
#         "EEVDF": "results/udf_8_8_eevdf.csv",
#         "RR":    "results/udf_8_8_rr.csv",
#         "UFS":   "results/udf_8_8_ufs.csv"
#     },
#     "16 YCSB vs 8 UDFs": {
#         "EEVDF": "results/udf_16_8_eevdf.csv",
#         "RR":    "results/udf_16_8_rr.csv",
#         "UFS":   "results/udf_16_8_ufs.csv"
#     },
#     "24 YCSB vs 8 UDFs": {
#         "EEVDF": "results/udf_24_8_eevdf.csv",
#         "RR":    "results/udf_24_8_rr.csv",
#         "UFS":   "results/udf_24_8_ufs.csv"
#     },
#     "32 YCSB vs 8 UDFs": {
#         "EEVDF": "results/udf_32_8_eevdf.csv",
#         "RR":    "results/udf_32_8_rr.csv",
#         "UFS":   "results/udf_32_8_ufs.csv"
#     }
# }
###########################################



### CONFIGURATION 4
### TPC-C EXPERIMENT: PERFORMANCE OF EEVDF AND UFS UNDER MIXED-PRIORITIES
groups = {
    "filename": "plot_mixed_priorities.pdf",
    "mixes": {
        "6667:2": {
            "EEVDF":        "results/client_8_8_tpcc_eevdf_prio_mix_low.csv",
            "UFS":          "results/client_8_8_tpcc_ufs_prio_mix_low.csv"
        },
        "10000:3": {
            "EEVDF":        "results/client_8_8_tpcc_eevdf_prio_mix_high.csv",
            "UFS":          "results/client_8_8_tpcc_ufs_prio_mix_high.csv",
        },
    }
}

udf_groups = {
    "6667:2": {
        "EEVDF":        "results/udf_16_16_eevdf_split_lw.csv",
        "UFS":          "results/udf_16_16_ufs_split_lw.csv"
    },
    "10000:3": {
        "EEVDF":        "results/udf_16_16_eevdf_split_lw_high.csv",
        "UFS":          "results/udf_16_16_ufs_split_lw_high.csv"
    }
}


### CONFIGURATION 5
### TPC-C EXPERIMENT: PERFORMANCE OF EEVDF AND UFS FOR ML WORKLOADS
# groups = {
#     "filename": "plot_madlib.pdf",
#     "mixes": {
#         "SOLO": {
#             "EEVDF":        "results/client_8_0_tpcc_eevdf.csv",
#             "UFS":          "results/client_8_0_tpcc_ufs.csv",
#             "RR":           "results/client_8_0_tpcc_rr.csv"
#         },
#         "MIN:MAX": {
#             "EEVDF":        "results/client_8_8_tpcc_eevdf_madlib.csv",
#             "UFS":          "results/client_8_8_tpcc_ufs_madlib.csv",
#             "RR":           "results/client_8_8_tpcc_rr_madlib.csv"
#         },
#         "50:50": {
#             "EEVDF":        "results/client_8_8_tpcc_eevdf_madlib_same_prio.csv",
#             "UFS":          "results/client_8_8_tpcc_ufs_madlib_same_prio.csv",
#             "RR":           "results/client_8_8_tpcc_rr_madlib_same_prio.csv"
#         }
#     }
# }
# udf_groups = {
#     "SOLO": {
#             "EEVDF":        "results/madlib_0_8_eevdf.csv",
#             "UFS":          "results/madlib_0_8_eevdf.csv",
#             "RR":           "results/madlib_0_8_eevdf.csv"
#         },
#     "MIN:MAX": {
#         "EEVDF":        "results/madlib_8_8_eevdf.csv",
#         "UFS":          "results/madlib_8_8_ufs.csv",
#         "RR":           "results/madlib_8_8_rr.csv",
#     },
#     "50:50": {
#         "EEVDF":        "results/madlib_8_8_eevdf_same_prio.csv",
#         "UFS":          "results/madlib_8_8_ufs_same_prio.csv",
#         "RR":           "results/madlib_8_8_rr_same_prio.csv",
#     },
# }




def formDataFrame(filename):
    data = pd.read_csv(filename)
    df = pd.DataFrame(data)

    print(filename)
    df['timestamp_us'] = df['Start Time (microseconds)']
    df['timestamp_us'] = df['timestamp_us'] - df['timestamp_us'].iloc[0]
    df['Latency (microseconds)'] = df['Latency (microseconds)'] / 1000.0

    total_time_sec = 60
    total_ops = len(df)
    throughput = total_ops / total_time_sec if total_time_sec > 0 else 0

    return df, throughput


def read_udf_throughput(filename: str) -> float:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError(f"Empty throughput file: {filename}")

    token = content.split()[0]
    return float(token)


def format_tput(v: float) -> str:
    if abs(v - round(v)) < 0.05:
        return f"{int(round(v))}"
    return f"{v:.1f}"


def nice_tick_step(max_val: float) -> float:
    if max_val <= 0:
        return 1.0

    rough = max_val / 4.0
    magnitude = 10 ** np.floor(np.log10(rough))

    for multiplier in (1, 2, 2.5, 5, 10):
        step = multiplier * magnitude
        if rough <= step:
            return float(step)

    return float(10 * magnitude)


if "filename" not in groups:
    raise KeyError("groups must define a top-level 'filename' field")

if "mixes" not in groups:
    raise KeyError("groups must define a top-level 'mixes' field")

output_filename = groups["filename"]
groups = groups["mixes"]


parser = argparse.ArgumentParser()
parser.add_argument(
    "--details",
    action="store_true",
    help="Show the latency table and plot title."
)
args = parser.parse_args()

show_details = args.details
has_udf = bool(udf_groups)

if has_udf and list(groups.keys()) != list(udf_groups.keys()):
    raise ValueError("groups and udf_groups must define the same group names in the same order")


def policy_present_everywhere(policy: str) -> bool:
    """
    A policy is active only if it is present in every client group,
    and, when UDF data is enabled, every UDF group as well.
    Missing policies are ignored instead of causing the script to fail.
    """
    if any(policy not in file_dict for file_dict in groups.values()):
        return False

    if has_udf and any(policy not in file_dict for file_dict in udf_groups.values()):
        return False

    return True


active_policy_labels = [
    policy for policy in policy_labels
    if policy_present_everywhere(policy)
]

ignored_policy_labels = [
    policy for policy in policy_labels
    if policy not in active_policy_labels
]

if not active_policy_labels:
    raise ValueError("No policies from policy_labels are present in the selected experiment")

if ignored_policy_labels:
    print(f"Ignoring missing policies: {', '.join(ignored_policy_labels)}")


stats = {g: {} for g in groups.keys()}
udf_stats = {g: {} for g in udf_groups.keys()} if has_udf else {}
table_rows = []

for group_name, file_dict in groups.items():
    for policy in active_policy_labels:
        csv_path = file_dict[policy]
        df, tput = formDataFrame(csv_path)

        rec = {
            "tput": int(tput),
        }

        if show_details:
            series = df['Latency (microseconds)'].dropna().to_numpy()
            if series.size == 0:
                raise ValueError(f"No latency values found in file: {csv_path}")

            rec["mean"] = float(np.mean(series))
            rec["p50"] = float(np.quantile(series, 0.50))
            rec["p95"] = float(np.quantile(series, 0.95))

            table_rows.append([
                f"{group_name} - {policy}",
                f"{rec['mean']:.2f}",
                f"{rec['p50']:.2f}",
                f"{rec['p95']:.2f}",
            ])

        stats[group_name][policy] = rec

if has_udf:
    for group_name, file_dict in udf_groups.items():
        for policy in active_policy_labels:
            csv_path = file_dict[policy]
            udf_tput = read_udf_throughput(csv_path)

            udf_stats[group_name][policy] = {
                "tput": float(udf_tput),
            }

group_names = list(groups.keys())
num_groups = len(group_names)
num_policies = len(active_policy_labels)

x = np.arange(num_groups)
total_width = 0.78
bar_width = total_width / num_policies
start = -total_width / 2 + bar_width / 2

if show_details:
    if has_udf:
        fig, axes = plt.subplots(
            nrows=2,
            ncols=1,
            gridspec_kw={'height_ratios': [4.4, 1.7]},
            figsize=(16, 11)
        )
    else:
        fig, axes = plt.subplots(
            nrows=2,
            ncols=1,
            gridspec_kw={'height_ratios': [3.6, 1.5]},
            figsize=(16, 10)
        )
    ax = axes[0]
    table_ax = axes[1]
else:
    fig, ax = plt.subplots(figsize=(16, 8 if has_udf else 6.5))
    table_ax = None

client_global_max = 0.0
udf_global_max = 0.0

client_legend_handles = {}
udf_legend_handles = {}

for pi, policy in enumerate(active_policy_labels):
    client_vals = [stats[group_name][policy]["tput"] for group_name in group_names]
    offsets = x + (start + pi * bar_width)

    client_bars = ax.bar(
        offsets,
        client_vals,
        bar_width,
        label=policy if not has_udf else f"{policy}/{benchmark}",
        color=policy_colors[policy]
    )

    ax.bar_label(
        client_bars,
        labels=[format_tput(v) for v in client_vals],
        padding=4,
        fontsize=14
    )

    client_legend_handles[policy] = client_bars[0]

    if has_udf:
        udf_vals = [udf_stats[group_name][policy]["tput"] for group_name in group_names]

        udf_bars = ax.bar(
            offsets,
            [-v for v in udf_vals],
            bar_width,
            label=f"{policy}/{udf_label}",
            color=policy_colors[policy],
            hatch="//",
            edgecolor="black",
            linewidth=1.0,
        )

        ax.bar_label(
            udf_bars,
            labels=[format_tput(v) for v in udf_vals],
            padding=4,
            fontsize=14
        )

        udf_legend_handles[policy] = udf_bars[0]
        udf_global_max = max(udf_global_max, max(udf_vals))

    client_global_max = max(client_global_max, max(client_vals))

if has_udf:
    ax.axhline(0, color="black", linewidth=1.2)

ax.set_xticks(x)
ax.set_xticklabels(group_names, fontsize=17, rotation=10, ha="right")
ax.set_ylabel("Throughput (ops/sec)", fontsize=20)
ax.tick_params(axis="y", labelsize=16)

if show_details:
    if has_udf:
        ax.set_title(f"{benchmark} and {udf_label} Throughput w.r.t. clients ({clients} CPUs)", fontsize=20)
    else:
        ax.set_title(f"{benchmark} Raw Throughput w.r.t. clients ({clients} CPUs)", fontsize=20)

if has_udf:
    ax.text(
        0.01,
        0.98,
        benchmark,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=17,
    )
    ax.text(
        0.01,
        0.02,
        udf_label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=17,
    )

ax.grid(axis="y", alpha=0.35)

if has_udf:
    legend_handles = []
    legend_labels = []

    for policy in active_policy_labels:
        legend_handles.extend([
            client_legend_handles[policy],
            udf_legend_handles[policy],
        ])
        legend_labels.extend([
            f"{policy}/{benchmark}",
            f"{policy}/{udf_label}",
        ])

    ax.legend(
        legend_handles,
        legend_labels,
        fontsize=15,
        ncols=num_policies,
        loc="upper center"
    )

    pos_limit = client_global_max * 1.22
    neg_limit = udf_global_max * 1.45
    ax.set_ylim(-neg_limit, pos_limit)

    step = nice_tick_step(max(pos_limit, neg_limit))
    neg_tick_extent = np.ceil(neg_limit / step) * step
    pos_tick_extent = np.ceil(pos_limit / step) * step
    neg_ticks = np.arange(-neg_tick_extent, 0, step)
    pos_ticks = np.arange(0, pos_tick_extent + step * 0.5, step)
    ax.set_yticks(np.concatenate([neg_ticks, pos_ticks]))
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: format_tput(abs(y)))
    )
else:
    ax.legend(fontsize=15)
    ax.set_ylim(0, client_global_max * 1.18)

if show_details:
    columns = [
        "Measure",
        "Mean latency (ms)",
        "p50 latency (ms)",
        "p95 latency (ms)",
    ]

    table_ax.axis("off")
    table = table_ax.table(
        cellText=table_rows,
        colLabels=columns,
        loc="center"
    )

    table.auto_set_font_size(False)
    for (i, j), cell in table.get_celld().items():
        if j == 0:
            cell.set_width(0.50)
        else:
            cell.set_width(0.16)

        if i == 0:
            cell.set_height(0.15)
            cell.set_text_props(weight="bold", fontsize=15)
        else:
            cell.set_height(0.11)
            cell.set_text_props(fontsize=13)

    table.scale(1, 1.2)
    plt.tight_layout(rect=(0, 0.02, 1, 0.98))
else:
    plt.tight_layout()

out_path = os.path.join("sched_ext/barplot", output_filename)

os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, format="pdf")
print(f"Saved: {out_path}")

os.system(f'brave "{out_path}"')
# plt.show()