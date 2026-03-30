import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


def formDataFrame(filename):
    data = pd.read_csv(filename)
    df = pd.DataFrame(data)

    df["timestamp"] = df["Start Time (microseconds)"] // 1
    df["Latency (microseconds)"] = df["Latency (microseconds)"] / 1000.0
    df["timestamp"] = df["timestamp"] - df["timestamp"].iloc[0]

    total_time_sec = 60
    total_ops = len(df)
    throughput = total_ops / total_time_sec if total_time_sec > 0 else 0

    return df, throughput


parser = argparse.ArgumentParser()
parser.add_argument(
    "--details",
    action="store_true",
    help="Show the plot title and latency table."
)
args = parser.parse_args()

show_details = args.details

bench = "TPC-C"
udf = "TPC-H UDFs"
subject = "Latency"
key = "Latency (microseconds)"
clients = "8"

df_eevdf, t_eevdf = formDataFrame("results/client_8_8_tpcc_eevdf.csv")
df_fifo, t_fifo = formDataFrame("results/client_8_8_tpcc_rr.csv")
df_sched, t_sched = formDataFrame("results/client_8_8_tpcc_ufs.csv")

keyword_eevdf = "EEVDF"
keyword_sched = "UFS"
keyword_fifo = "Round-Robin"

policy_colors = {
    "EEVDF": "#66c2a5",
    "Round-Robin": "#fc8d62",
    "UFS": "#8da0cb",
}

if show_details:
    fig, ax1 = plt.subplots(figsize=(24, 13))
else:
    fig, ax1 = plt.subplots(figsize=(20, 10))

box_data = [df_eevdf[key], df_fifo[key].values, df_sched[key].values]
box_labels = [keyword_eevdf, keyword_fifo, keyword_sched]

bp = ax1.boxplot(
    box_data,
    labels=box_labels,
    whis=(5, 95),
    showfliers=False,
    patch_artist=True,
    widths=0.55
)

for patch, label in zip(bp["boxes"], box_labels):
    patch.set_facecolor(policy_colors[label])
    patch.set_edgecolor("black")
    patch.set_alpha(0.9)

for whisker in bp["whiskers"]:
    whisker.set_color("black")
    whisker.set_linewidth(2.2)

for cap in bp["caps"]:
    cap.set_color("black")
    cap.set_linewidth(2.2)

for median in bp["medians"]:
    median.set_color("black")
    median.set_linewidth(1.5)

y95 = max(
    np.percentile(box_data[0], 95),
    np.percentile(box_data[1], 95),
    np.percentile(box_data[2], 95),
)
ax1.set_ylim(0, y95 * 1.05)

ax1.set_xlabel(f"Scheduling Policy ({clients} {bench} against {clients} {udf})", fontsize=18, labelpad=10)
ax1.set_ylabel("TPC-C Query Latency", fontsize=18)

plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

if show_details:
    plt.title(
        f"{subject} with different scheduling policies - {bench} Benchmark ({clients} clients)",
        fontsize=20,
        pad=10
    )

ax1.grid(axis="y", alpha=0.35)

if show_details:
    fig.subplots_adjust(left=0.08, right=0.985, top=0.90, bottom=0.36)
else:
    fig.subplots_adjust(left=0.08, right=0.985, top=0.97, bottom=0.16)

for label, series in zip(box_labels, box_data):
    lo, hi = np.percentile(series, [5, 95])
    hidden = int(((series < lo) | (series > hi)).sum())
    print(f"{label} — hidden (outside 5–95%): {hidden} points")

if show_details:
    data = [
        [keyword_eevdf, f"{df_eevdf[key].mean():.2f}", f"{df_eevdf[key].quantile(0.95):.2f}", f"{t_eevdf:.2f}"],
        [keyword_fifo, f"{df_fifo[key].mean():.2f}", f"{df_fifo[key].quantile(0.95):.2f}", f"{t_fifo:.2f}"],
        [keyword_sched, f"{df_sched[key].mean():.2f}", f"{df_sched[key].quantile(0.95):.2f}", f"{t_sched:.2f}"],
    ]
    columns = ["Measure", "Mean latency (ms)", "95th Percentile latency (ms)", "Throughput (tps)"]

    table_ax = fig.add_axes([0.08, 0.05, 0.84, 0.22])
    table_ax.axis("off")
    table = table_ax.table(cellText=data, colLabels=columns, loc="center")

    table.auto_set_font_size(False)
    for (i, j), cell in table.get_celld().items():
        if j == 0:
            cell.set_width(0.34)
        else:
            cell.set_width(0.18)

        if i == 0:
            cell.set_height(0.16)
            cell.set_text_props(weight="bold", fontsize=14)
        else:
            cell.set_height(0.14)
            cell.set_text_props(fontsize=14)

    table.scale(1, 1.0)

out_path = f"sched_ext/boxplot/{bench}{subject}_{udf}_{clients}_latency.pdf"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
plt.savefig(out_path, format="pdf", bbox_inches="tight", pad_inches=0.05)

#os.system(f'brave "{out_path}"')
plt.show()