import matplotlib.pyplot as plt
import numpy as np
import os
import sys


# ============================================================
# PARSER
# ============================================================
def parse_file(path):
    partitions = {}
    partition_vals = []
    current_part = None

    with open(path) as f:
        for line in f:
            line = line.strip()

            if ".part." in line:
                if current_part is not None:
                    partitions[current_part] = partition_vals
                current_part = line.split(".part.")[-1]
                partition_vals = []

            elif line.startswith("Pid") and "Vol:" in line:
                val = int(line.split("Vol:")[-1].strip())
                partition_vals.append(val)

        if current_part is not None:
            partitions[current_part] = partition_vals

    return partitions


# ============================================================
# FILE MATCHING
# ============================================================
def extract_graph_id(filename):
    prefixes = [
        "vol_partitions_",
        "nvol_08_",
    ]

    suffixes = [
        "_graph_volpartitions",
        "_graph_partitions",
    ]

    for suffix in suffixes:
        if filename.endswith(suffix):
            core = filename[: -len(suffix)]

            for prefix in prefixes:
                if core.startswith(prefix):
                    core = core[len(prefix):]
                    break

            return core if core else None

    return None

def find_matching_files(folder_a, folder_b):
    files_a = {}
    files_b = {}

    for f in os.listdir(folder_a):
        gid = extract_graph_id(f)
        if gid:
            files_a[gid] = f

    for f in os.listdir(folder_b):
        gid = extract_graph_id(f)
        if gid:
            files_b[gid] = f

    common_ids = sorted(set(files_a.keys()) & set(files_b.keys()))

    if not common_ids:
        raise RuntimeError(
            "No matching graph IDs found.\n"
            f"Folder A IDs: {sorted(files_a.keys())}\n"
            f"Folder B IDs: {sorted(files_b.keys())}"
        )

    return [(gid, files_a[gid], files_b[gid]) for gid in common_ids]


# ============================================================
# PLOTTING
# ============================================================
def plot_partition(dict_a, dict_b, partition_key, title_a="Folder A", title_b="Folder B"):
    if partition_key not in dict_a or partition_key not in dict_b:
        available = sorted(set(dict_a.keys()) & set(dict_b.keys()), key=lambda k: int(k))
        raise ValueError(
            f"Partition '{partition_key}' not found.\n"
            f"Available partitions: {available}"
        )

    a = dict_a[partition_key]
    b = dict_b[partition_key]

    if len(a) != len(b):
        raise ValueError(f"Length mismatch in partition {partition_key}")

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(a))
    width = 0.35

    ax.bar(x - width / 2, a, width, label=title_a)
    ax.bar(x + width / 2, b, width, label=title_b)

    ax.set_title(f"Partition {partition_key}")
    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in range(len(a))])
    ax.set_ylabel("Volume")
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.legend()

    plt.tight_layout()
    plt.show()


# ============================================================
# MAIN
# ============================================================
def main():

    if len(sys.argv) != 4:
        print("Usage: python graph_results_vol.py <graph_id> <partition_nr> <version>")
        print("Example: python graph_results_vol.py 100_cube 4 nvol_08")
        sys.exit(1)

    version = sys.argv[3]
    folder_a = f"output_stats/vol_partitions_partitions/incoming_vol/"
    folder_b = f"output_stats/{version}_partitions/incoming_vol/"


    graph_id = sys.argv[1]
    partition_nr = sys.argv[2]

    matches = find_matching_files(folder_a, folder_b)
    match = next((m for m in matches if m[0] == graph_id), None)

    if match is None:
        available = [m[0] for m in matches]
        raise RuntimeError(
            f"Graph '{graph_id}' not found in both folders.\n"
            f"Available graphs: {available}"
        )

    tmp, file_a, file_b = match

    print(f"[INFO] Comparing graph: {graph_id}, partition: {partition_nr}")

    dict_a = parse_file(os.path.join(folder_a, file_a))
    dict_b = parse_file(os.path.join(folder_b, file_b))

    plot_partition(
        dict_a, dict_b,
        partition_key=partition_nr,
        title_a="METIS",
        title_b=f"{version}"
    )


if __name__ == "__main__":
    main()