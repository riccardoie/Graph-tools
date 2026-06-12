import re
import matplotlib.pyplot as plt
from pathlib import Path


# ---- CONFIG ----4 
filter_name = "unfiltered_boundaries"
versions = ["rg-mk_25_03", "cut"]

# the EXACT stats filename you want to plot
stats_filename = "channel-500x100x100-b050_graph_partition_stats"

base_path = Path("output_stats")


def parse_single_file(file_path):
    partitions = []
    total = []
    max_cut = []
    avg = []
    std = []

    with open(file_path, "r") as f:
        content = f.read()

    pattern = re.findall(
        r"\.part\.(\d+).*?"
        r"Total Edge Cut:\s+([\d.]+).*?"
        r"Max Edge Cut:\s+([\d.]+).*?"
        r"Average Edge Cut:\s+([\d.]+).*?"
        r"Std.Dev:\s+([\d.]+)",
        content,
        re.S
    )

    for p, t, m, a, s in pattern:
        partitions.append(int(p))
        total.append(float(t))
        max_cut.append(float(m))
        avg.append(float(a))
        std.append(float(s))

    # sort by partition number
    combined = sorted(zip(partitions, total, max_cut, avg, std))
    partitions, total, max_cut, avg, std = zip(*combined)

    return partitions, total, max_cut, avg, std


data = {}

for version in versions:
    if(version == "cut" or version == "vol"):
        stats_path = (
            base_path
            / f"{version}_partitions"
            / "stats"
            / stats_filename
        )
    else:
        stats_path = (
            base_path
            / filter_name
            / f"{version}_partitions"
            / "stats"
            / stats_filename
        )


    if not stats_path.exists():
        raise FileNotFoundError(stats_path)

    data[version] = parse_single_file(stats_path)


# -----------------------------
# Chart 1 — Average / Max / Std
# -----------------------------

plt.figure(figsize=(10, 6))

for version in versions:
    partitions, _, max_cut, avg, std = data[version]

    plt.plot(partitions, avg, marker="o", label=f"{version} Avg")
    plt.plot(partitions, max_cut, linestyle="--", marker="s", label=f"{version} Max")
    plt.plot(partitions, std, linestyle=":", marker="^", label=f"{version} Std")

plt.xlabel("Partitions")
plt.ylabel("Edge Cut")
plt.title("Edge Cut Metrics vs Partitions")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


# -----------------------------
# Chart 2 — Total Edge Cut
# -----------------------------

plt.figure(figsize=(10, 6))

for version in versions:
    partitions, total, *_ = data[version]
    plt.plot(partitions, total, marker="o", linewidth=2, label=version)

plt.xlabel("Partitions")
plt.ylabel("Total Edge Cut")
plt.title("Total Edge Cut vs Partitions")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()


import numpy as np

metrics = [
    ("Total Edge Cut", 1),
    ("Max Edge Cut", 2),
    ("Average Edge Cut", 3),
    ("Std.Dev", 4),
]

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
axes = axes.flatten()

bar_width = 0.25

# assume all versions share the same partitions
partitions = data[versions[0]][0]
x = np.arange(len(partitions))


for ax, (metric_name, metric_index) in zip(axes, metrics):

    for i, version in enumerate(versions):
        metric_values = data[version][metric_index]

        ax.bar(
            x + i * bar_width,
            metric_values,
            width=bar_width,
            label=version
        )

    ax.set_title(metric_name)
    ax.set_xticks(x + bar_width)
    ax.set_xticklabels(partitions)
    ax.set_xlabel("Partitions")
    ax.grid(axis='y', alpha=0.3)


# Only one legend for the entire figure
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
