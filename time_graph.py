#!/usr/bin/env python3
import os
import re
import sys
import matplotlib.pyplot as plt

# --- Parse arguments ---
if len(sys.argv) != 3:
    print("Usage: python compare.py <path_to_A_stats> <path_to_B_stats>")
    sys.exit(1)

DIR_A = f"../{sys.argv[1]}_partitions/stats"
DIR_B = f"../{sys.argv[2]}_partitions/stats"

# Regex to extract timing values
pattern = {
    "io": re.compile(r"I/O Time:\s*([\d.]+)"),
    "partition": re.compile(r"Partition Time:\s*([\d.]+)"),
    "reporting": re.compile(r"Reporting Time:\s*([\d.]+)")
}

# Regex for numbers
first_num_re = re.compile(r"^(\d+)")
second_num_re = re.compile(r"graph_(\d+)_stats(?:\.txt)?$")

def is_cube(filename):
    """True if filename contains '_cube_graph_'."""
    return "_cube_graph_" in filename

def parse_filename_numbers(filename):
    """Extract (first_number, second_number)."""
    m1 = first_num_re.search(filename)
    if not m1:
        n1 = -1
    else:
        n1 = int(m1.group(1))

    m2 = second_num_re.search(filename)
    if not m2:
        return (n1, 999999)
    n2 = int(m2.group(1))

    return (n1, n2)

def parse_stats(filepath):
    """Extract timing fields and compute total."""
    with open(filepath, "r") as f:
        text = f.read()

    m_io = pattern["io"].search(text)
    m_part = pattern["partition"].search(text)
    m_rep = pattern["reporting"].search(text)

    if not (m_io and m_part and m_rep):
        raise ValueError(f"Missing required fields in {filepath}")

    io = float(m_io.group(1))
    part = float(m_part.group(1))
    rep = float(m_rep.group(1))
    return io, part, rep, io + part + rep

def compute_differences(file_list):
    """Compute percentage change arrays for a group."""
    labels = []
    pct_total = []
    pct_io = []
    pct_part = []
    pct_rep = []

    for fname in file_list:
        a_path = os.path.join(DIR_A, fname)
        b_path = os.path.join(DIR_B, fname)

        io_a, part_a, rep_a, total_a = parse_stats(a_path)
        io_b, part_b, rep_b, total_b = parse_stats(b_path)

        # Use percentage change, avoid division by zero
        pct_io.append(((io_a - io_b) / io_b * 100) if io_b != 0 else 0)
        pct_part.append(((part_a - part_b) / part_b * 100) if part_b != 0 else 0)
        pct_rep.append(((rep_a - rep_b) / rep_b * 100) if rep_b != 0 else 0)
        pct_total.append(((total_a - total_b) / total_b * 100) if total_b != 0 else 0)

        labels.append(fname)  # Use filename as x-axis label

    return labels, pct_total, pct_io, pct_part, pct_rep


def plot_group(title, labels, dt, io, pt, rp, type1, type2):
    """Generate plot for one set."""
    if not labels:
        print(f"No data for: {title}")
        return

    plt.figure(figsize=(15, 6))
    plt.plot(labels, dt, label=f"Total Time (%) ({type1} vs {type2})", linewidth=2)
    plt.plot(labels, io, label=f"I/O Time Diff ({type1} − {type2})")
    plt.plot(labels, pt, label=f"Partition Time Diff ({type1} − {type2})")
    plt.plot(labels, rp, label=f"Reporting Time Diff ({type1} − {type2})")

    plt.xticks(rotation=90)
    plt.xlabel("(graph size, nr of partitions)")
    plt.ylabel("Percentage Change (%)")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    files_a = [f for f in os.listdir(DIR_A) if os.path.isfile(os.path.join(DIR_A, f))]
    files_b = [f for f in os.listdir(DIR_B) if os.path.isfile(os.path.join(DIR_B, f))]

    common = sorted(set(files_a) & set(files_b))

    cube_files = sorted([f for f in common if is_cube(f)], key=parse_filename_numbers)
    normal_files = sorted([f for f in common if not is_cube(f)], key=parse_filename_numbers)

    # non-cube
    lbl_n, dt_n, io_n, pt_n, rp_n = compute_differences(normal_files,)
    # cube
    lbl_c, dt_c, io_c, pt_c, rp_c = compute_differences(cube_files)

    plot_group("Timing Differences — GRID Graphs", lbl_n, dt_n, io_n, pt_n, rp_n, sys.argv[1], sys.argv[2])
    plot_group("Timing Differences — CUBE Graphs", lbl_c, dt_c, io_c, pt_c, rp_c, sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
