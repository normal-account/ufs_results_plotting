#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os


############# CONFIGURATION ###############
policy_labels = ["EEVDF", "UFS"]

policy_colors = {
    "EEVDF": "#e6e6e6",
    "UFS": "#9ccc65",
}

categories = ["Throughput", "Wakeup Latency", "Request Latency"]

values = {
    "EEVDF": [7908, 3156, 33472],
    "UFS":   [8118,  507, 12464],
}

output_file = "throughput_wakeup_request_latency_barplot_bigtext.pdf"
###########################################


def format_value(v: float) -> str:
    if abs(v - round(v)) < 0.05:
        return f"{int(round(v))}"
    return f"{v:.1f}"


x = np.arange(len(categories))
total_width = 0.72
bar_width = total_width / len(policy_labels)
start = -total_width / 2 + bar_width / 2

fig, ax = plt.subplots(figsize=(10, 6))

global_max = 0.0

for pi, policy in enumerate(policy_labels):
    vals = values[policy]
    offsets = x + (start + pi * bar_width)

    bars = ax.bar(
        offsets,
        vals,
        bar_width,
        label=policy,
        color=policy_colors[policy],
        edgecolor="black",
        linewidth=1.0,
    )

    ax.bar_label(
        bars,
        labels=[format_value(v) for v in vals],
        padding=4,
        fontsize=13
    )

    global_max = max(global_max, max(vals))

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=15)
ax.set_ylabel("Throughput (req/s) / p99.9 Latency (μs)", fontsize=18)
ax.tick_params(axis="y", labelsize=15)
ax.legend(fontsize=15)
ax.grid(axis="y", alpha=0.35)
ax.set_ylim(0, global_max * 1.18)

plt.tight_layout()
plt.savefig(output_file, format="pdf")
print(f"Saved: {output_file}")
#os.system(f'brave "{output_file}"')
plt.show()
