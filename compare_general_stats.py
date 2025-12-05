#!/usr/bin/env python3
import os
import re
import sys
import csv
import matplotlib.pyplot as plt

# --- Parse arguments ---
if len(sys.argv) != 3:
    print("Usage: python compare_cut_comm.py <path_to_A_stats> <path_to_B_stats>")
    sys.exit(1)

DIR_A = f"../{sys.argv[1]}_partitions/stats"
DIR_B = f"../{sys.argv[2]}_partitions/stats"

# Regex to extract the fields
edgecut_re = re.compile(r"Edgecut:\s*([\d.]+)")
commvol_re = re.compile(r"Communication Vol\.\s*:\s*([\d.]+)")

# Filename parsing regexes
first_num_re = re.compile(r"^(\d+)")
second_num_re = re.compile(r"graph_(\d+)_stats(?:\.txt)?$")

def parse_filename_numbers(filename):
    """Extract (first_number, second_number) for sorting."""
    m1 = first_num_re.search(filename)
    if not m1:
        return (999999, 999999)

    n1 = int(m1.group(1))

    m2 = second_num_re.search(filename)
    if not m2:
        return (n1, 999999)

    n2 = int(m2.group(1))
    return (n1, n2)

def parse_stats(filepath):
    """Extract Edgecut and Communication Volume."""
    with open(filepath, "r") as f:
        text = f.read()

    m_edge = edgecut_re.search(text)
    m_comm = commvol_re.search(text)

    if not (m_edge and m_comm):
        raise ValueError(f"Missing fields in {filepath}")

    edge = float(m_edge.group(1))
    comm = float(m_comm.group(1))
    return edge, comm

def main():
    # Load files
    files_a = [f for f in os.listdir(DIR_A) if os.path.isfile(os.path.join(DIR_A, f))]
    files_b = [f for f in os.listdir(DIR_B) if os.path.isfile(os.path.join(DIR_B, f))]

    # Intersect
    common = sorted(set(files_a) & set(files_b))

    # Sort by numeric (first, second)
    common.sort(key=parse_filename_numbers)

    # Containers
    labels = []
    edge_a = []
    edge_b = []
    comm_a = []
    comm_b = []

    # --- Prepare CSV ---
    csv_rows = []
    csv_header = [
        "filename",
        f"edgecut_{sys.argv[1]}", f"edgecut_{sys.argv[2]}", "diff_edgecut",
        f"comm_{sys.argv[1]}", f"comm_{sys.argv[2]}", "diff_comm"
    ]

    for fname in common:
        a_path = os.path.join(DIR_A, fname)
        b_path = os.path.join(DIR_B, fname)

        ea, ca = parse_stats(a_path)
        eb, cb = parse_stats(b_path)

        edge_a.append(ea)
        edge_b.append(eb)
        comm_a.append(ca)
        comm_b.append(cb)

        csv_rows.append([
            fname,
            ea, eb, eb - ea,
            ca, cb, cb - ca
        ])

    # --- Write CSV ---
    with open("comparison_output.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)

    print("CSV file written: comparison_output.csv")

    # --- Plot percent differences ---
    filenames = []
    pct_edge = []
    pct_comm = []

    with open("comparison_output.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filenames.append(row["filename"])

            ea = float(row[f"edgecut_{sys.argv[1]}"])
            eb = float(row[f"edgecut_{sys.argv[2]}"])
            ca = float(row[f"comm_{sys.argv[1]}"])
            cb = float(row[f"comm_{sys.argv[2]}"])

            pct_edge.append((eb - ea) / ea * 100 if ea != 0 else 0)
            pct_comm.append((cb - ca) / ca * 100 if ca != 0 else 0)

    plt.figure(figsize=(15, 6))
    plt.plot(filenames, pct_edge, marker="o", label="Edgecut % Difference")
    plt.plot(filenames, pct_comm, marker="s", label="Comm Volume % Difference")

    plt.title(f"Percentual Difference Between {sys.argv[1]} and {sys.argv[2]}")
    plt.ylabel("Percent Difference (%)")
    plt.xlabel("Filename")
    plt.xticks(rotation=90)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.text(
    0.01, 0.95,
        f"Positive % means {sys.argv[2]} is worse than {sys.argv[1]}\nNegative % means {sys.argv[2]} is better than {sys.argv[1]}",
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
