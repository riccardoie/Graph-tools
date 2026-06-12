# import re
# import numpy as np
# import matplotlib.pyplot as plt
# from pathlib import Path


# # --------------------
# # CONFIG
# # --------------------
# versions = ["vol_partitions", "nvol_08"]

# version_labels = {
#     "vol_partitions": "METIS",
#     "nvol_08": "NVOL",
# }

# # List of graphs to compare
# graphs = [
#     "heart01",
#     "heart02",
#     "heart03",
#     "heart04",
#     "heart05",
#     "heart06",
#     "heart06",
#     "heart07",
#     # "hugetric-00000",
# ]

# # Single partition number to plot
# target_partition = 2

# base_path = Path("output_stats")


# # --------------------
# # PARSER (VOLUME ONLY)
# # --------------------
# def parse_volume_file(file_path):
#     partitions, total, max_vol, avg, std = [], [], [], [], []

#     with open(file_path, "r") as f:
#         content = f.read()

#     pattern = re.findall(
#         r"\.part\.(\d+).*?"
#         r"Total Volume:\s+([\d.]+).*?"
#         r"Max Volume:\s+([\d.]+).*?"
#         r"Average Volume:\s+([\d.]+).*?"
#         r"Std.Dev:\s+([\d.]+)",
#         content,
#         re.S,
#     )

#     if not pattern:
#         raise ValueError(f"No volume data parsed from {file_path}")

#     for p, t, m, a, s in pattern:
#         partitions.append(int(p))
#         total.append(float(t))
#         max_vol.append(float(m))
#         avg.append(float(a))
#         std.append(float(s))

#     combined = sorted(zip(partitions, total, max_vol, avg, std))
#     partitions, total, max_vol, avg, std = map(list, zip(*combined))

#     return partitions, total, max_vol, avg, std


# def get_metric_at_partition(parsed, partition_nr, metric_index):
#     """metric_index: 1=total, 2=max_vol, 3=avg, 4=std"""
#     partitions = parsed[0]
#     if partition_nr not in partitions:
#         return None
#     idx = partitions.index(partition_nr)
#     return parsed[metric_index][idx]


# # --------------------
# # LOAD DATA
# # --------------------
# # data[graph][version] = parsed tuple
# data = {}
# missing = []

# for graph in graphs:
#     data[graph] = {}
#     stats_filename = f"{graph}_graph_partition_stats"

#     for version in versions:
#         stats_path = base_path / f"{version}_partitions" / "stats" / stats_filename

#         if not stats_path.exists():
#             print(f"WARNING: missing {stats_path}")
#             missing.append((graph, version))
#             data[graph][version] = None
#             continue

#         try:
#             data[graph][version] = parse_volume_file(stats_path)
#         except ValueError as e:
#             print(f"WARNING: {e}")
#             data[graph][version] = None
#             missing.append((graph, version))


# # Keep only graphs where every version has the target partition
# valid_graphs = []
# for graph in graphs:
#     ok = True
#     for version in versions:
#         parsed = data[graph][version]
#         if parsed is None or target_partition not in parsed[0]:
#             ok = False
#             break
#     if ok:
#         valid_graphs.append(graph)

# if not valid_graphs:
#     raise ValueError(
#         f"No graphs have data for partition {target_partition} across all versions"
#     )

# dropped = set(graphs) - set(valid_graphs)
# if dropped:
#     print(f"Dropped graphs (missing partition {target_partition}): {dropped}")


# # -----------------------------
# # CHART — Bar Comparison Across Graphs
# # -----------------------------
# # Three subplots side by side:
# #   Std.Dev | Max Volume | Max Volume Improvement vs METIS (%)
# metrics = [
#     ("Std.Dev", 4),
#     ("Max Volume", 2),
#     ("Max Volume Improvement vs METIS (%)", "improvement"),
# ]

# fig, axes = plt.subplots(1, 3, figsize=(20, 6))

# bar_width = 0.35
# x = np.arange(len(valid_graphs))

# for ax, (metric_name, metric_index) in zip(axes, metrics):
#     if metric_index == "improvement":
#         # Only NVOL versions plotted as improvement vs METIS baseline
#         nvol_versions = [v for v in versions if v != "vol_partitions"]
#         improvement_width = 0.6 if len(nvol_versions) == 1 else bar_width

#         for i, version in enumerate(nvol_versions):
#             base_max = np.array([
#                 get_metric_at_partition(data[g]["vol_partitions"], target_partition, 2)
#                 for g in valid_graphs
#             ])
#             current_max = np.array([
#                 get_metric_at_partition(data[g][version], target_partition, 2)
#                 for g in valid_graphs
#             ])
#             improvement = ((base_max - current_max) / base_max) * 100

#             offset = i * bar_width if len(nvol_versions) > 1 else 0
#             bars = ax.bar(
#                 x + offset,
#                 improvement,
#                 width=improvement_width,
#                 label=version_labels[version],
#                 color=f"C{versions.index(version)}",
#             )
#             # annotate values
#             for b, v in zip(bars, improvement):
#                 ax.text(
#                     b.get_x() + b.get_width() / 2,
#                     b.get_height(),
#                     f"{v:.1f}%",
#                     ha="center",
#                     va="bottom",
#                     fontsize=9,
#                 )

#         ax.axhline(0, color="black", linewidth=0.8)
#         tick_offset = (
#             bar_width / 2 * (len(nvol_versions) - 1) if len(nvol_versions) > 1 else 0
#         )
#     else:
#         for i, version in enumerate(versions):
#             metric_values = [
#                 get_metric_at_partition(data[g][version], target_partition, metric_index)
#                 for g in valid_graphs
#             ]
#             ax.bar(
#                 x + i * bar_width,
#                 metric_values,
#                 width=bar_width,
#                 label=version_labels[version],
#                 color=f"C{i}",
#             )
#         tick_offset = bar_width / 2 * (len(versions) - 1)

#     ax.set_title(metric_name)
#     ax.set_xticks(x + tick_offset)
#     ax.set_xticklabels(valid_graphs, rotation=30, ha="right")
#     ax.set_xlabel("Graph")
#     ax.grid(axis="y", alpha=0.3)

# handles, labels = axes[0].get_legend_handles_labels()
# fig.suptitle(
#     f"Heart dataset {target_partition} partitions",
#     fontsize=16,
#     fontweight="bold",
# )
# fig.legend(handles, labels, loc="upper right", ncol=len(versions))

# plt.tight_layout(rect=[0, 0, 1, 0.94])
# plt.show()

# import re
# import numpy as np
# import matplotlib.pyplot as plt
# from pathlib import Path


# # --------------------
# # CONFIG
# # --------------------
# versions = ["vol_partitions", "nvol_08"]

# version_labels = {
#     "vol_partitions": "VOL",
#     "nvol_08": "NVOL",
# }

# # List of graphs to compare
# graphs = [
#     "heart01",
#     "heart02",
#     "heart03",
#     "heart04",
#     "heart05",
#     "heart06",
#     "heart07",
#     # "hugetric-00000",
# ]

# # Single partition number to plot
# target_partition = 2

# base_path = Path("output_stats")
# output_file = Path(f"../../Thesis/pictures/stddev_comparison_p{target_partition}.pdf")


# # --------------------
# # PARSER (VOLUME ONLY)
# # --------------------
# def parse_volume_file(file_path):
#     partitions, total, max_vol, avg, std = [], [], [], [], []

#     with open(file_path, "r") as f:
#         content = f.read()

#     pattern = re.findall(
#         r"\.part\.(\d+).*?"
#         r"Total Volume:\s+([\d.]+).*?"
#         r"Max Volume:\s+([\d.]+).*?"
#         r"Average Volume:\s+([\d.]+).*?"
#         r"Std.Dev:\s+([\d.]+)",
#         content,
#         re.S,
#     )

#     if not pattern:
#         raise ValueError(f"No volume data parsed from {file_path}")

#     for p, t, m, a, s in pattern:
#         partitions.append(int(p))
#         total.append(float(t))
#         max_vol.append(float(m))
#         avg.append(float(a))
#         std.append(float(s))

#     combined = sorted(zip(partitions, total, max_vol, avg, std))
#     partitions, total, max_vol, avg, std = map(list, zip(*combined))

#     return partitions, total, max_vol, avg, std


# def get_metric_at_partition(parsed, partition_nr, metric_index):
#     """metric_index: 1=total, 2=max_vol, 3=avg, 4=std"""
#     partitions = parsed[0]
#     if partition_nr not in partitions:
#         return None
#     idx = partitions.index(partition_nr)
#     return parsed[metric_index][idx]


# # --------------------
# # LOAD DATA
# # --------------------
# data = {}

# for graph in graphs:
#     data[graph] = {}
#     stats_filename = f"{graph}_graph_partition_stats"

#     for version in versions:
#         stats_path = base_path / f"{version}_partitions" / "stats" / stats_filename

#         if not stats_path.exists():
#             print(f"WARNING: missing {stats_path}")
#             data[graph][version] = None
#             continue

#         try:
#             data[graph][version] = parse_volume_file(stats_path)
#         except ValueError as e:
#             print(f"WARNING: {e}")
#             data[graph][version] = None


# valid_graphs = []
# for graph in graphs:
#     ok = True
#     for version in versions:
#         parsed = data[graph][version]
#         if parsed is None or target_partition not in parsed[0]:
#             ok = False
#             break
#     if ok:
#         valid_graphs.append(graph)

# if not valid_graphs:
#     raise ValueError(
#         f"No graphs have data for partition {target_partition} across all versions"
#     )

# dropped = set(graphs) - set(valid_graphs)
# if dropped:
#     print(f"Dropped graphs (missing partition {target_partition}): {dropped}")


# # -----------------------------
# # CHART — Std.Dev / Avg
# # -----------------------------
# fig, ax = plt.subplots(figsize=(10, 6))

# bar_width = 0.35
# x = np.arange(len(valid_graphs))

# for i, version in enumerate(versions):
#     std_values = [
#         get_metric_at_partition(data[g][version], target_partition, 4)
#         for g in valid_graphs
#     ]
#     avg_values = [
#         get_metric_at_partition(data[g][version], target_partition, 3)
#         for g in valid_graphs
#     ]
#     metric_values = [
#         s / a if a else 0 for s, a in zip(std_values, avg_values)
#     ]
#     ax.bar(
#         x + i * bar_width,
#         metric_values,
#         width=bar_width,
#         label=version_labels[version],
#         color=f"C{i}",
#     )

# ax.set_title(f"Std.Dev / Avg Volume Heart dataset k={target_partition}")
# ax.set_xticks(x + bar_width / 2 * (len(versions) - 1))
# ax.set_xticklabels(valid_graphs, rotation=30, ha="right")
# ax.set_xlabel("Graph")
# ax.set_ylabel("Std.Dev / Avg Volume")
# ax.grid(axis="y", alpha=0.3)
# ax.legend()

# plt.tight_layout()
# plt.savefig(output_file, dpi=300, bbox_inches="tight")
# plt.show()

import re
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# --------------------
# CONFIG
# --------------------
versions = ["vol_partitions", "nvol_08"]

# Geometric graphs to compare
graphs = [
    "pa2010",
    "delaunay_n23",
    "delaunay_n24",
    "rgg_n_2_23_s0"    
]

base_path = Path("output_stats")
output_file = Path("../../Thesis/pictures/geometric_max_vol_diff.pdf")


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

for graph in graphs:
    data[graph] = {}
    stats_filename = f"{graph}_graph_partition_stats"

    for version in versions:
        stats_path = base_path / f"{version}_partitions" / "stats" / stats_filename

        if not stats_path.exists():
            print(f"WARNING: missing {stats_path}")
            data[graph][version] = None
            continue

        try:
            data[graph][version] = parse_volume_file(stats_path)
        except ValueError as e:
            print(f"WARNING: {e}")
            data[graph][version] = None


# -----------------------------
# CHART — % difference of Max Volume vs k, one line per graph
# -----------------------------
fig, ax = plt.subplots(figsize=(10, 6))

for graph in graphs:
    metis_data = data[graph]["vol_partitions"]
    nvol_data = data[graph]["nvol_08"]

    if metis_data is None or nvol_data is None:
        print(f"Skipping {graph}: missing data")
        continue

    # Find partitions present in both versions
    metis_parts = set(metis_data[0])
    nvol_parts = set(nvol_data[0])
    common = sorted(metis_parts & nvol_parts)

    metis_idx = {p: i for i, p in enumerate(metis_data[0])}
    nvol_idx = {p: i for i, p in enumerate(nvol_data[0])}

    # (METIS - NVOL) / METIS * 100, on max volume (index 2)
    diffs = []
    for k in common:
        m = metis_data[2][metis_idx[k]]
        n = nvol_data[2][nvol_idx[k]]
        diffs.append((m - n) / m * 100)

    ax.plot(common, diffs, marker="o", label=graph)

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xscale("log", base=2)
ax.set_xticks([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048])
ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax.set_xlabel("Partitions (k)")
ax.set_ylabel("Max outgoing volume — % difference (NVOL vs VOL)")
ax.set_title("Geometric graphs: percentage difference of maximum outgoing volume for different k")
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"Saved plot to {output_file}")
plt.show()