import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# --------------------
# CONFIG
# --------------------
versions = ["vol_partitions", "nvol_08"] #, "nvol_08_4"

# Display names for the legend / titles
version_labels = {
    "vol_partitions": "VOL",
    "nvol_08": "NVOL",
    # "nvol_08_4": "NVOL 4%",
}

file = "heart06_graph_"
file = "delaunay_n24_graph_"
# # file = "packing-500x100x100-b050_graph_"
# # # # file = "roadNet-CA_graph_"
# # file = "channel-500x100x100-b050_graph_"
# # # file = "citationCiteseer_graph_"
# # # file = "fe_tooth_graph_"
# file = "coPapersDBLP_graph_"
# # file = "italy_osm_graph_"
# file = "hugetric-00000_graph_"
# # file = "europe_osm_graph_"
# file = "delaunay_n23_graph_"
# file = "rgg_n_2_23_s0_graph_"
file = "pa2010_graph_"
# # # file = "hugetric-00020_graph_"
# # file = "hugetrace-00020_graph_"
# file = "kmer_V2a_graph_"
# file = "kmer_U1a_graph_"

stats_filename = file + "partition_stats"
vol_filename = file + "partition_stats"
base_path = Path("output_stats")

graph_name = file.rstrip("_")


# --------------------
# PARSER (VOLUME ONLY)
# --------------------
def parse_volume_file(file_path):
    partitions, total, max_vol, avg, std = [], [], [], [], []

    with open(file_path, "r") as f:
        content = f.read()

    pattern = re.findall(
        r"\.part\.(\d+).*?"
        r"Total Volume:\s+([\d.]+).*?"
        r"Max Volume:\s+([\d.]+).*?"
        r"Average Volume:\s+([\d.]+).*?"
        r"Std.Dev:\s+([\d.]+)",
        content,
        re.S,
    )

    if not pattern:
        raise ValueError(f"No volume data parsed from {file_path}")

    for p, t, m, a, s in pattern:
        partitions.append(int(p))
        total.append(float(t))
        max_vol.append(float(m))
        avg.append(float(a))
        std.append(float(s))

    combined = sorted(zip(partitions, total, max_vol, avg, std))
    partitions, total, max_vol, avg, std = map(list, zip(*combined))

    return partitions, total, max_vol, avg, std


# --------------------
# LOAD DATA
# --------------------
data = {}

for version in versions:
    if version == "vol_partitions":
        stats_path = base_path / f"{version}_partitions" / "stats" / vol_filename
    else:
        stats_path = base_path / f"{version}_partitions" / "stats" / stats_filename

    print(stats_path)
    if not stats_path.exists():
        raise FileNotFoundError(stats_path)

    data[version] = parse_volume_file(stats_path)


# -----------------------------
# CHART — Bar Comparison
# -----------------------------
# Layout (row-major):
#   (0,0) Total Volume          (0,1) Std.Dev
#   (1,0) Max Volume            (1,1) Max Volume Improvement vs METIS
metrics = [
    ("Std.Dev / Avg Volume", "stddev_norm"),
    ("Total Volume", 1),
    # ("Std.Dev", 4),
    ("Max Volume", 2),
    ("Max Volume Improvement vs VOL (%)", "improvement"),
]

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
axes = axes.flatten()
# fig, axes = plt.subplots(1, 1, figsize=(8, 5))
# fig, axes = plt.subplots(1, 2, figsize=(14, 5))
# axes = [axes]  # wrap so zip(axes, metrics) still works

bar_width = 0.3

# Use only partitions common to all versions
partition_sets = [set(data[v][0]) for v in versions]
common_partitions = sorted(set.intersection(*partition_sets))

if not common_partitions:
    raise ValueError("No common partitions across all versions")

index_maps = {v: {p: i for i, p in enumerate(data[v][0])} for v in versions}
x = np.arange(len(common_partitions))

for ax, (metric_name, metric_index) in zip(axes, metrics):
    for i, version in enumerate(versions):
        idxs = [index_maps[version][p] for p in common_partitions]

        if metric_index == "improvement":
            if version == "vol_partitions":
                metric_values = np.zeros(len(common_partitions))
            else:
                vol_idxs = [index_maps["vol_partitions"][p] for p in common_partitions]
                base_max = np.array([data["vol_partitions"][2][j] for j in vol_idxs])
                current_max = np.array([data[version][2][j] for j in idxs])
                metric_values = ((base_max - current_max) / base_max) * 100
        elif metric_index == "stddev_norm":
            std_vals = np.array([data[version][4][j] for j in idxs])
            avg_vals = np.array([data[version][3][j] for j in idxs])
            metric_values = np.divide(
                std_vals, avg_vals,
                out=np.zeros_like(std_vals),
                where=avg_vals != 0,
            )
        else:
            metric_values = [data[version][metric_index][j] for j in idxs]

        ax.bar(
            x + i * bar_width,
            metric_values,
            width=bar_width,
            label=version_labels[version],
        )

    ax.set_title(metric_name)
    ax.set_xticks(x + bar_width / 2 * (len(versions) - 1))
    ax.set_xticklabels(common_partitions)
    ax.set_xlabel("Partitions")
    ax.grid(axis="y", alpha=0.3)

handles, labels = axes[0].get_legend_handles_labels()
fig.suptitle(graph_name, fontsize=16, fontweight="bold")
fig.legend(handles, labels, loc="upper left", ncol=len(versions))

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()

# print(metric_values)
print(" & ".join(f"{x:.2f}" for x in metric_values))