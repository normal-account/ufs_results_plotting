import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


############# CONFIGURATION ###############
benchmark = "IWL"
udf_label = "BWL"
policy_labels = ["EEVDF", "RR", "UFS"]
clients = "8"

policy_colors = {
    "EEVDF": "#e6e6e6",
    "RR": "#d493b8",
    "UFS": "#9ccc65",
}

###########################################


########### TEMPLATE CONFIG ###############

# UNCOMMENT THE BELOW CONFIGURATIONS DEPENDING ON THE EXPERIMENT TO PLOT.

### CONFIGURATION 1
### TPC-C EXPERIMENT: PERFORMANCE OF THE 3 SCHEDULERS UNDER DIFFERENT SETTINGS
groups = {
    "SOLO": {
        "EEVDF":        "results/client_8_0_tpcc_eevdf.csv",
        "RR":  "results/client_8_0_tpcc_rr.csv",
        "UFS":          "results/client_8_0_tpcc_ufs.csv"
    },
    "MIN:MAX": {
        "EEVDF":        "results/client_8_8_tpcc_eevdf.csv",
        "RR":  "results/client_8_8_tpcc_rr.csv",
        "UFS":          "results/client_8_8_tpcc_ufs.csv"
    },
    "50:50 MIX": {
        "EEVDF":        "results/client_8_8_tpcc_eevdf_same_prio.csv",
        "RR":  "results/client_8_8_tpcc_rr_same_prio.csv",
        "UFS":          "results/client_8_8_tpcc_ufs_same_prio.csv"
    }
}

udf_groups = {
    "SOLO": {
        "EEVDF":        "results/udf_0_8_eevdf.csv",
        "RR":  "results/udf_0_8_rr.csv",
        "UFS":          "results/udf_0_8_ufs.csv"
    },
    "MIN:MAX": {
        "EEVDF":        "results/udf_8_8_eevdf.csv",
        "RR":  "results/udf_8_8_rr.csv",
        "UFS":          "results/udf_8_8_ufs.csv"
    },
    "50:50 MIX": {
        "EEVDF":        "results/udf_8_8_eevdf_same_prio.csv",
        "RR":  "results/udf_8_8_rr_same_prio.csv",
        "UFS":          "results/udf_8_8_ufs_same_prio.csv"
    }
}

### CONFIGURATION 2
### TPC-C EXPERIMENT: THROUGHPUT W.R.T. NUMBER OF CLIENTS (OVERSUBSCRIPTION)
# groups = {
#     "8B/8I": {
#         "EEVDF": "results/client_8_8_tpcc_eevdf.csv",
#         "RR":    "results/client_8_8_tpcc_rr.csv",
#         "UFS":   "results/client_8_8_tpcc_ufs.csv"
#     },
#     "8B/16I": {
#         "EEVDF": "results/client_16_8_tpcc_eevdf.csv",
#         "RR":    "results/client_16_8_tpcc_rr.csv",
#         "UFS":   "results/client_16_8_tpcc_ufs.csv"
#     },
#     "8B/24I": {
#         "EEVDF": "results/client_24_8_tpcc_eevdf.csv",
#         "RR":    "results/client_24_8_tpcc_rr.csv",
#         "UFS":   "results/client_24_8_tpcc_ufs.csv"
#     },
#     # "32 TPC-C vs 8 UDFs": {
#     #     "EEVDF":        "results/client_32_8_tpcc_eevdf.csv",
#     #     "RR":  "results/client_32_8_tpcc_rr.csv",
#     #     "UFS":          "results/client_32_8_tpcc_ufs.csv"
#     # }
# }

# udf_groups = {

# }

### CONFIGURATION 3
### YCSB EXPERIMENT: THROUGHPUT W.R.T NUMBER OF CLIENTS (OVERSUBSCRIPTION)
# benchmark = "YCSB"
# groups = {
#     "Baseline (8 YCSB vs 8 UDFs)": {
#         "EEVDF":        "results/client_8_8_ycsb_eevdf.csv",
#         "RR":  "results/client_8_8_ycsb_rr.csv",
#         "UFS":          "results/client_8_8_ycsb_ufs.csv"
#     },
#     "16 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/client_16_8_ycsb_eevdf.csv",
#         "RR":  "results/client_16_8_ycsb_rr.csv",
#         "UFS":          "results/client_16_8_ycsb_ufs.csv"
#     },
#     "24 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/client_24_8_ycsb_eevdf.csv",
#         "RR":  "results/client_24_8_ycsb_rr.csv",
#         "UFS":          "results/client_24_8_ycsb_ufs.csv"
#     },
#     "32 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/client_32_8_ycsb_eevdf.csv",
#         "RR":  "results/client_32_8_ycsb_rr.csv",
#         "UFS":          "results/client_32_8_ycsb_ufs.csv"
#     }
# }
#
# udf_groups = {
#     "Baseline (8 YCSB vs 8 UDFs)": {
#         "EEVDF":        "results/udf_8_8_eevdf.csv",
#         "RR":  "results/udf_8_8_rr.csv",
#         "UFS":          "results/udf_8_8_ufs.csv"
#     },
#     "16 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/udf_16_8_eevdf.csv",
#         "RR":  "results/udf_16_8_rr.csv",
#         "UFS":          "results/udf_16_8_ufs.csv"
#     },
#     "24 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/udf_24_8_eevdf.csv",
#         "RR":  "results/udf_24_8_rr.csv",
#         "UFS":          "results/udf_24_8_ufs.csv"
#     },
#     "32 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/udf_32_8_eevdf.csv",
#         "RR":  "results/udf_32_8_rr.csv",
#         "UFS":          "results/udf_32_8_ufs.csv"
#     }
# }
###########################################


def formDataFrame(filename):
    data = pd.read_csv(filename)
    df = pd.DataFrame(data)

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

stats = {g: {} for g in groups.keys()}
udf_stats = {g: {} for g in udf_groups.keys()} if has_udf else {}
table_rows = []

for group_name, file_dict in groups.items():
    for policy in policy_labels:
        if policy not in file_dict:
            raise KeyError(f"Group '{group_name}' missing policy '{policy}' in groups[...] mapping")

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
        for policy in policy_labels:
            if policy not in file_dict:
                raise KeyError(f"Group '{group_name}' missing policy '{policy}' in udf_groups[...] mapping")

            csv_path = file_dict[policy]
            udf_tput = read_udf_throughput(csv_path)

            udf_stats[group_name][policy] = {
                "tput": float(udf_tput),
            }

group_names = list(groups.keys())
num_groups = len(group_names)
num_policies = len(policy_labels)

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
legend_handles = []
legend_labels = []

for pi, policy in enumerate(policy_labels):
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

        legend_handles.extend([client_bars[0], udf_bars[0]])
        legend_labels.extend([f"{policy}/{benchmark}", f"{policy}/{udf_label}"])
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
    ax.legend(legend_handles, legend_labels, fontsize=15, ncols=3, loc="upper center")

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

group_suffix = "_".join(groups.keys()).replace(" ", "_").replace("/", "_")
if has_udf:
    out_path = f"sched_ext/barplot/barplot_{group_suffix}_{benchmark}_sched_client_udf_{clients}.pdf"
else:
    out_path = f"sched_ext/barplot/barplot_{group_suffix}_{benchmark}_sched_client_{clients}.pdf"

os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, format="pdf")
print(f"Saved: {out_path}")

#os.system(f'brave "{out_path}"')
plt.show()
