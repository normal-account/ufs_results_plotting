import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


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


def format_tput(v: float) -> str:
    if abs(v - round(v)) < 0.05:
        return f"{int(round(v))}"
    return f"{v:.1f}"


parser = argparse.ArgumentParser()
parser.add_argument(
    "--details",
    action="store_true",
    help="Show the latency table and plot title."
)
args = parser.parse_args()

show_details = args.details


# =====================================================================
# TEMPLATE CONFIG
# UNCOMMENT THE BELOW CONFIGURATIONS DEPENDING ON THE EXPERIMENT TO PLOT.

### CONFIGURATION 1
### TPC-C EXPERIMENT: PERFORMANCE OF THE 3 SCHEDULERS UNDER DIFFERENT SETTINGS
groups = {
    "Baseline (8 TPC-C)": {
        "EEVDF":        "results/client_8_0_tpcc_eevdf.csv",
        "Round-Robin":  "results/client_8_0_tpcc_rr.csv",
        "UFS":          "results/client_8_0_tpcc_ufs.csv"
    },
    "8 high-priority TPC-C vs 8 low-priority TPC-H UDFs": {
        "EEVDF":        "results/client_8_8_tpcc_eevdf.csv",
        "Round-Robin":  "results/client_8_8_tpcc_rr.csv",
        "UFS":          "results/client_8_8_tpcc_ufs.csv"
    },
    "8 TPC-C vs 8 TPC-H UDFs, equal priorities": {
        "EEVDF":        "results/client_8_8_tpcc_eevdf_same_prio.csv",
        "Round-Robin":  "results/client_8_8_tpcc_rr_same_prio.csv",
        "UFS":          "results/client_8_8_tpcc_ufs_same_prio.csv"
    }
}

### CONFIGURATION 2
### TPC-C EXPERIMENT: THROUGHPUT W.R.T. NUMBER OF CLIENTS (OVERSUBSCRIPTION)
# groups = {
#     "Baseline (8 TPC-C vs 8 UDFs)": {
#         "EEVDF":        "results/client_8_8_tpcc_eevdf.csv",
#         "Round-Robin":  "results/client_8_8_tpcc_rr.csv",
#         "UFS":          "results/client_8_8_tpcc_ufs.csv"
#     },
#     "16 TPC-C vs 8 UDFs": {
#         "EEVDF":        "results/client_16_8_tpcc_eevdf.csv",
#         "Round-Robin":  "results/client_16_8_tpcc_rr.csv",
#         "UFS":          "results/client_16_8_tpcc_ufs.csv"
#     },
#     "24 TPC-C vs 8 UDFs": {
#         "EEVDF":        "results/client_24_8_tpcc_eevdf.csv",
#         "Round-Robin":  "results/client_24_8_tpcc_rr.csv",
#         "UFS":          "results/client_24_8_tpcc_ufs.csv"
#     },
#     # "32 TPC-C vs 8 UDFs": {
#     #     "EEVDF":        "results/client_32_8_tpcc_eevdf.csv",
#     #     "Round-Robin":  "results/client_32_8_tpcc_rr.csv",
#     #     "UFS":          "results/client_32_8_tpcc_ufs.csv"
#     # }
# }

### CONFIGURATION 3
### YCSB EXPERIMENT: THROUGHPUT W.R.T NUMBER OF CLIENTS (OVERSUBSCRIPTION)
# groups = {
#     "Baseline (8 YCSB vs 8 UDFs)": {
#         "EEVDF":        "results/client_8_8_ycsb_eevdf.csv",
#         "Round-Robin":  "results/client_8_8_ycsb_rr.csv",
#         "UFS":          "results/client_8_8_ycsb_ufs.csv"
#     },
#     "16 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/client_16_8_ycsb_eevdf.csv",
#         "Round-Robin":  "results/client_16_8_ycsb_rr.csv",
#         "UFS":          "results/client_16_8_ycsb_ufs.csv"
#     },
#     "24 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/client_24_8_ycsb_eevdf.csv",
#         "Round-Robin":  "results/client_24_8_ycsb_rr.csv",
#         "UFS":          "results/client_24_8_ycsb_ufs.csv"
#     },
#     "32 YCSB vs 8 UDFs": {
#         "EEVDF":        "results/client_32_8_ycsb_eevdf.csv",
#         "Round-Robin":  "results/client_32_8_ycsb_rr.csv",
#         "UFS":          "results/client_32_8_ycsb_ufs.csv"
#     }
# }

### CHANGE THE BELOW VALUES AS NEEDED.
benchmark = "TPC-C"
policy_labels = ["EEVDF", "Round-Robin", "UFS"]
clients = "8"

policy_colors = {
    "EEVDF": "#66c2a5",
    "Round-Robin": "#fc8d62",
    "UFS": "#8da0cb",
}
# =====================================================================

stats = {g: {} for g in groups.keys()}
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

group_names = list(groups.keys())
num_groups = len(group_names)
num_policies = len(policy_labels)

x = np.arange(num_groups)
total_width = 0.78
bar_width = total_width / num_policies
start = -total_width / 2 + bar_width / 2

if show_details:
    fig, axes = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={'height_ratios': [3.6, 1.5]},
        figsize=(16, 10)
    )
    ax = axes[0]
    table_ax = axes[1]
else:
    fig, ax = plt.subplots(figsize=(16, 6.5))
    table_ax = None

global_max = 0.0

for pi, policy in enumerate(policy_labels):
    vals = [stats[group_name][policy]["tput"] for group_name in group_names]
    offsets = x + (start + pi * bar_width)

    bars = ax.bar(
        offsets,
        vals,
        bar_width,
        label=policy,
        color=policy_colors[policy]
    )

    ax.bar_label(
        bars,
        labels=[format_tput(v) for v in vals],
        padding=3,
        fontsize=10
    )

    global_max = max(global_max, max(vals))

ax.set_xticks(x)
ax.set_xticklabels(group_names, fontsize=12, rotation=10, ha="right")
ax.set_ylabel(f"{benchmark} Throughput", fontsize=14)
if show_details:
    ax.set_title(f"{benchmark} Raw Throughput w.r.t. clients ({clients} CPUs)", fontsize=16)
ax.grid(axis="y", alpha=0.35)
ax.legend(fontsize=11)
ax.set_ylim(0, global_max * 1.18)

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
            cell.set_text_props(weight="bold", fontsize=11)
        else:
            cell.set_height(0.11)
            cell.set_text_props(fontsize=10)

    table.scale(1, 1.15)
    plt.tight_layout(rect=(0, 0.02, 1, 0.98))
else:
    plt.tight_layout()

group_suffix = "_".join(groups.keys()).replace(" ", "_").replace("/", "_")
out_path = f"sched_ext/barplot/barplot_{group_suffix}_{benchmark}_sched_client_{clients}.pdf"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, format="pdf")
print(f"Saved: {out_path}")

#os.system(f'brave "{out_path}"')
plt.show()