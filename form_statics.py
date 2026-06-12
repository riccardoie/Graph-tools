import os 
import statistics
from statistics import pstdev
import re
import csv

def form_stats(folder):
    source_folder =f"output_stats/{folder}_partitions"

    partitions = {}
    for partition_file in os.listdir(source_folder):        
        if not  os.path.isfile(f"{source_folder}/{partition_file}"):
            continue
        
        with open(f"{source_folder}/{partition_file}","r") as f:
            for line in f:
                line = line.strip()

                # Detect partition header
                if ".part." in line:
                    current_part = line
                    partitions[current_part] = []

                elif line.startswith("Pid"):
                    value = int(line.split(":")[1].strip())
                    partitions[current_part].append(value)

        filename = partition_file[len(folder) + 1:-1] + "_stats"
        write_csv(partitions,folder, filename)
        partitions = {}



def compute_stats(values, type):
    if (type == "cut_partitions" or "rg-mk" in type):
        return {
            "total_edge_cut": sum(values) / 2,
            "max_edge_cut": max(values),
            "average_edge_cut": statistics.mean(values),
            "std_dev": statistics.pstdev(values)  # population std dev
        }
    else:
        return {
            "total_volume": sum(values),
            "max_volume": max(values),
            "average_volume": statistics.mean(values),
            "std_dev": statistics.pstdev(values)  # population std dev
        }

def extract_part_number(part_name):
    return int(re.search(r"\.part\.(\d+)", part_name).group(1))

def write_csv(partitions, folder, output_file):

    source_folder =f"output_stats/{folder}_partitions/stats"

    os.makedirs(source_folder, exist_ok=True)
    # Sort partitions by part number
    sorted_parts = sorted(partitions.items(), key=lambda x: extract_part_number(x[0]))

    with open(f"{source_folder}/{output_file}", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if (folder == "cut_partitions" or "rg-mk" in folder):
            for part, values in sorted_parts:
                stats = compute_stats(values, folder)
                writer.writerow([part])
                writer.writerow([f"\tTotal Edge Cut: \t{stats["total_edge_cut"]}"])
                writer.writerow([f"\tMax Edge Cut: \t\t{stats["max_edge_cut"]}"])
                writer.writerow([f"\tAverage Edge Cut: \t{round(stats["average_edge_cut"], 2)}"])
                writer.writerow([f"\tStd.Dev: \t\t\t{round(stats["std_dev"], 2)}"])
                writer.writerow([])
        else:
            for part, values in sorted_parts:
                stats = compute_stats(values, folder)
                writer.writerow([part])
                writer.writerow([f"\tTotal Volume: \t\t{stats["total_volume"]}"])
                writer.writerow([f"\tMax Volume: \t\t{stats["max_volume"]}"])
                writer.writerow([f"\tAverage Volume: \t{round(stats["average_volume"], 2)}"])
                writer.writerow([f"\tStd.Dev: \t\t\t{round(stats["std_dev"], 2)}"])
                writer.writerow([])           



def graph_stats(graph):

    path = f"../graphs/{graph}_graph"

    with open(path, "r") as f:
        # Skip blank lines and comments to find the header.
        header = None
        for line in f:
            s = line.strip()
            if not s or s.startswith("%"):
                continue
            header = s.split()
            break
        if header is None:
            raise ValueError("Empty METIS file (no header found).")

        n = int(header[0])
        fmt = header[2].zfill(3) if len(header) >= 3 else "000"
        ncon = int(header[3]) if len(header) >= 4 else 1

        has_vsize = fmt[0] == "1"
        has_vwgt  = fmt[1] == "1"
        has_ewgt  = fmt[2] == "1"

        counts = []
        for line in f:
            # IMPORTANT: do NOT skip blank lines here — a blank line is a
            # legitimate vertex with zero neighbors. Only skip comments.
            if line.lstrip().startswith("%"):
                continue

            tokens = line.split()  # empty line -> []

            idx = 0
            if has_vsize:
                idx += 1
            if has_vwgt:
                idx += ncon
            payload = tokens[idx:]

            nbr_count = len(payload) // 2 if has_ewgt else len(payload)
            counts.append(nbr_count)

            if len(counts) == n:
                break

        if len(counts) != n:
            raise ValueError(
                f"Header declared {n} vertices, but only {len(counts)} "
                f"adjacency lines were found."
            )
        
        n_max = max(counts)
        n_min = min(counts)
        # Population std dev — every vertex is observed, not a sample.
        sigma = pstdev(counts) if len(counts) > 1 else 0.0
        mean = sum(counts) / len(counts)
        print(graph)
        print(f"Vertices       : {len(counts)}")
        print(f"Max neighbors  : {n_max}")
        print(f"Min neighbors  : {n_min}")
        print(f"Mean neighbors : {mean:.4f}")
        print(f"Std dev (pop.) : {sigma:.4f}")


# "kron_g500-logn19"
# graph_stats("heart07")
# form_stats("vol")
# graph_stats("delaunay_n23")
# graph_stats("packing-500x100x100-b050")