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


# =====================================================================
# TEMPLATE CONFIG
# UNCOMMENT THE BELOW CONFIGURATIONS DEPENDING ON THE EXPERIMENT TO PLOT.

### CONFIGURATION 1
### TPC-C EXPERIMENT: PERFORMANCE OF THE 3 SCHEDULERS UNDER DIFFERENT SETTINGS
# groups = {
#     "Baseline (8 TPC-C)": {
#         "EEVDF":        "results/client_8_0_tpcc_eevdf.csv",
#         "Round-Robin":  "results/client_8_0_tpcc_rr.csv",
#         "UFS":          "results/client_8_0_tpcc_ufs.csv"
#     },
#     "8 high-priority TPC-C vs 8 low-priority UDFs": {
#         "EEVDF":        "results/client_8_8_tpcc_eevdf.csv",
#         "Round-Robin":  "results/client_8_8_tpcc_rr.csv",
#         "UFS":          "results/client_8_8_tpcc_ufs.csv"
#     },
#     "8 high-priority TPC-C vs 8 low-priority burn tasks": {
#         "EEVDF":        "results/client_8_8_tpcc_eevdf_external_burn.csv",
#         "Round-Robin":  "results/client_8_8_tpcc_rr_external_burn.csv",
#         "UFS":          "results/client_8_8_tpcc_ufs_external_burn.csv"
#     },

#     # WARNING! THE BELOW CSVs WERE GENERATED WITHOUT PG SYNCHRONOUS COMMITS AND ARE OUTDATED. TO RE-GENERATE.
#     "8 TPC-C vs 8 UDFs, equal priorities": {
#         "EEVDF":        "results/client_8_8_tpcc_eevdf_same_prio.csv",
#         "Round-Robin":  "results/client_8_8_tpcc_rr_same_prio.csv",
#         "UFS":          "results/client_8_8_tpcc_ufs_same_prio.csv"
#     }
# }

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
#     "32 TPC-C vs 8 UDFs": {
#         "EEVDF":        "results/client_32_8_tpcc_eevdf.csv",
#         "Round-Robin":  "results/client_32_8_tpcc_rr.csv",
#         "UFS":          "results/client_32_8_tpcc_ufs.csv"
#     }
# }

### CONFIGURATION 3
### YCSB EXPERIMENT: THROUGHPUT W.R.T NUMBER OF CLIENTS (OVERSUBSCRIPTION)
groups = {
    "Baseline (8 YCSB vs 8 UDFs)": {
        "EEVDF":        "results/client_8_8_ycsb_eevdf.csv",
        "Round-Robin":  "results/client_8_8_ycsb_rr.csv",
        "UFS":          "results/client_8_8_ycsb_ufs.csv"
    },
    "16 YCSB vs 8 UDFs": {
        "EEVDF":        "results/client_16_8_ycsb_eevdf.csv",
        "Round-Robin":  "results/client_16_8_ycsb_rr.csv",
        "UFS":          "results/client_16_8_ycsb_ufs.csv"
    },
    "24 YCSB vs 8 UDFs": {
        "EEVDF":        "results/client_24_8_ycsb_eevdf.csv",
        "Round-Robin":  "results/client_24_8_ycsb_rr.csv",
        "UFS":          "results/client_24_8_ycsb_ufs.csv"
    },
    "32 YCSB vs 8 UDFs": {
        "EEVDF":        "results/client_32_8_ycsb_eevdf.csv",
        "Round-Robin":  "results/client_32_8_ycsb_rr.csv",
        "UFS":          "results/client_32_8_ycsb_ufs.csv"
    }
}

### CHANGE THE BELOW VALUES AS NEEDED (most likely only benchmark name). 
benchmark = "YCSB"
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

        series = df['Latency (microseconds)'].dropna().to_numpy()
        if series.size == 0:
            raise ValueError(f"No latency values found in file: {csv_path}")

        mean_v = float(np.mean(series))
        p50_v = float(np.quantile(series, 0.50))
        p95_v = float(np.quantile(series, 0.95))

        rec = {
            "tput": float(tput),
            "mean": mean_v,
            "p50": p50_v,
            "p95": p95_v,
        }
        stats[group_name][policy] = rec

        table_rows.append([
            f"{group_name} - {policy}",
            f"{rec['mean']:.2f}",
            f"{rec['p50']:.2f}",
            f"{rec['p95']:.2f}",
        ])

group_names = list(groups.keys())
num_groups = len(group_names)
num_policies = len(policy_labels)

x = np.arange(num_groups)
total_width = 0.78
bar_width = total_width / num_policies
start = -total_width / 2 + bar_width / 2

fig, axes = plt.subplots(
    nrows=2,
    ncols=1,
    gridspec_kw={'height_ratios': [3.6, 1.5]},
    figsize=(16, 10)
)

ax = axes[0]
table_ax = axes[1]

global_max = 0.0

for pi, policy in enumerate(policy_labels):
    vals = [stats[group_name][policy]["tput"] for group_name in group_names]
    offsets = x + (start + pi * bar_width)

    ax.bar(
        offsets,
        vals,
        bar_width,
        label=policy,
        color=policy_colors[policy]
    )
    global_max = max(global_max, max(vals))

ax.set_xticks(x)
ax.set_xticklabels(group_names, fontsize=12, rotation=10, ha="right")
ax.set_ylabel("Throughput (ops/sec)", fontsize=14)
ax.set_title(f"{benchmark} Raw Throughput w.r.t. clients ({clients} CPUs)", fontsize=16)
ax.grid(axis="y", alpha=0.35)
ax.legend(fontsize=11)
ax.set_ylim(0, global_max * 1.12)

# Table with latency stats only
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

group_suffix = "_".join(groups.keys()).replace(" ", "_").replace("/", "_")
out_path = f"sched_ext/barplot/barplot_{group_suffix}_{benchmark}_sched_client_{clients}.pdf"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, format="pdf")

#os.system(f'brave "{out_path}"')
plt.show()