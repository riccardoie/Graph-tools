import os 
import statistics
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



form_stats("vol")
