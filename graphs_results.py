import matplotlib.pyplot as plt
from matplotlib import gridspec
import math
import numpy as np
import os
import sys

def parse_file (file):

    partitions = {}
    partition_cuts = []
    nr_of_partitions = 0
    total_ed = 0 

    with  open(f"output_stats/{file}") as file: 
        for line in file: 
            
            if (".part" in line):

                if nr_of_partitions != 0: 
                #     partition_cuts.append(total_ed/2)
                    partitions[nr_of_partitions] = partition_cuts

                nr_of_partitions = line[line.find("part.") + len("part."):].strip()
                total_ed = 0
                partition_cuts = []

            elif ("Pid" in line): 
                cut = int(line[line.find(":") + 2:].strip())
                total_ed += cut

                partition_cuts.append(cut)

        # partition_cuts.append(total_ed/2)
        partitions[nr_of_partitions] = partition_cuts


    return partitions
              
def find_files(file, type):
    partition_files = []
    for partition_file in os.listdir("output_stats/cut_partitions"):
        if(f"_{file}_" in partition_file):
            partition_files.append(partition_file)

    for partition_file in os.listdir(f"output_stats/{type}/rg-mk_18_02_partitions"):
        if(f"_{file}_" in partition_file):
            partition_files.append(partition_file)

    for partition_file in os.listdir(f"output_stats/{type}/rg-mk_19_01_partitions"):
        if(f"_{file}_" in partition_file):
            partition_files.append(partition_file)

    for partition_file in partition_files:
        if ("rg-mk_19_01" in partition_file):
            rg_mk_old = parse_file(f"{type}/rg-mk_19_01_partitions/{partition_file}")
        elif ("rg-mk_18_02" in partition_file): 
            rg_mk = parse_file(f"{type}/rg-mk_18_02_partitions/{partition_file}")
        elif ("cut" in partition_file): 
            cut = parse_file(f"cut_partitions/{partition_file}")

    compare_dicts_grid_3(rg_mk, rg_mk_old, cut, "RG-MK(18_02)", "RG-MK-OLD(19_01)", "CUT")

def compare_dicts_grid_3(
    dict_a, dict_b, dict_c,
    title_a='Approach A',
    title_b='Approach B',
    title_c='Approach C'
):
    # --- Validation ---
    if not (dict_a.keys() == dict_b.keys() == dict_c.keys()):
        raise ValueError("All dictionaries must have the same keys")

    # --- Sort keys numerically ---
    keys = sorted(dict_a.keys(), key=lambda k: float(k))

    # --- Separate small and large partitions ---
    small_keys = [k for k in keys if len(dict_a[k]) <= 15]
    large_keys = [k for k in keys if len(dict_a[k]) > 15]

    # --- Helper function for labeling ---
    def make_labels(n):
        return [str(i) for i in range(n)]

    # ==========================
    # SMALL PARTITIONS IN GRID
    # ==========================
    if small_keys:
        small_cols = 3
        small_rows = math.ceil(len(small_keys) / small_cols)

        fig = plt.figure(figsize=(16, small_rows * 4))
        gs = gridspec.GridSpec(small_rows, small_cols, figure=fig)

        for i, key in enumerate(small_keys):
            row = i // small_cols
            col = i % small_cols
            ax = fig.add_subplot(gs[row, col])

            values_a = dict_a[key]
            values_b = dict_b[key]
            values_c = dict_c[key]

            if not (len(values_a) == len(values_b) == len(values_c)):
                raise ValueError(f"Value lists for key '{key}' must have same length")

            x = np.arange(len(values_a))
            width = 0.25

            ax.bar(x - width, values_a, width, label=title_a)
            ax.bar(x,         values_b, width, label=title_b)
            ax.bar(x + width, values_c, width, label=title_c)

            ax.set_title(f'Partition {key}', fontsize=11)
            ax.set_xlabel('Index')
            ax.set_ylabel('Value')
            ax.set_xticks(x)
            ax.set_xticklabels(make_labels(len(values_a)))
            ax.grid(axis='y', linestyle='--', alpha=0.6)

        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper right', fontsize=10)
        fig.suptitle(
            'Partition Comparison Grid (Small Partitions)',
            fontsize=16,
            y=0.995
        )
        plt.tight_layout()
        plt.show()

    # ==========================
    # LARGE PARTITIONS IN SEPARATE WINDOWS
    # ==========================
    for key in large_keys:
        values_a = dict_a[key]
        values_b = dict_b[key]
        values_c = dict_c[key]

        if not (len(values_a) == len(values_b) == len(values_c)):
            raise ValueError(f"Value lists for key '{key}' must have same length")

        fig, ax = plt.subplots(figsize=(12, 5))
        x = np.arange(len(values_a))
        width = 0.25

        ax.bar(x - width, values_a, width, label=title_a)
        ax.bar(x,         values_b, width, label=title_b)
        ax.bar(x + width, values_c, width, label=title_c)

        ax.set_title(f'Partition {key}', fontsize=12)
        ax.set_xlabel('Partition Pid')
        ax.set_ylabel('Cut')
        ax.set_xticks(x)
        ax.set_xticklabels(make_labels(len(values_a)))
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.legend()

        plt.tight_layout()
        plt.show()



if __name__ == "__main__":
    # if len(sys.argv) < 3 or len(sys.argv) > 3:
    #     print(
    #         "Usage: python script.py <graph_file>"
    #     )
    #     sys.exit(1)
    
    graph_filename = sys.argv[1]
    type = sys.argv[2]    

    find_files(graph_filename, type)