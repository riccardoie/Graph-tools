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
                    partition_cuts.append(total_ed/2)
                    partitions[nr_of_partitions] = partition_cuts

                nr_of_partitions = line[line.find("part.") + len("part."):].strip()
                total_ed = 0
                partition_cuts = []

            elif ("Pid" in line): 
                cut = int(line[line.find(":") + 2:].strip())
                total_ed += cut

                partition_cuts.append(cut)

        partition_cuts.append(total_ed/2)
        partitions[nr_of_partitions] = partition_cuts


    return partitions
              
def find_files(file):

    partition_files = []
    for partition_file in os.listdir("output_stats"):
        if(f"_{file}_" in partition_file):
            partition_files.append(partition_file)

    for partition_file in partition_files:
        if ("rg-mk" in partition_file):
            rg_mk = parse_file(partition_file)
        else: 
            cut = parse_file(partition_file)

    # print(rg_mk)
    # print(cut)
    compare_dicts_grid(rg_mk, cut, "RG-MK", "CUT")


import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import math

def compare_dicts_grid(dict_a, dict_b, title_a='Approach A', title_b='Approach B'):
    # --- Validation ---
    if dict_a.keys() != dict_b.keys():
        raise ValueError("Both dictionaries must have the same keys")

    # --- Sort keys numerically ---
    keys = sorted(dict_a.keys(), key=lambda k: float(k))

    # --- Separate small and large partitions ---
    small_keys = [k for k in keys if len(dict_a[k]) <= 15]
    large_keys = [k for k in keys if len(dict_a[k]) > 15]

    # --- Helper function for labeling ---
    def make_labels(n):
        labels = [str(i) for i in range(n)]
        if n > 0:
            labels[-1] = "Total Cut"
        return labels

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

            values_a, values_b = dict_a[key], dict_b[key]
            if len(values_a) != len(values_b):
                raise ValueError(f"Value lists for key '{key}' must have same length")

            x = np.arange(len(values_a))
            width = 0.4
            ax.bar(x - width/2, values_a, width, label=title_a, color='skyblue')
            ax.bar(x + width/2, values_b, width, label=title_b, color='salmon')
            ax.set_title(f'Partition {key}', fontsize=11)
            ax.set_xlabel('Index')
            ax.set_ylabel('Value')
            ax.set_xticks(x)
            ax.set_xticklabels(make_labels(len(values_a)))
            ax.grid(axis='y', linestyle='--', alpha=0.6)

        handles, labels = ax.get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper right', fontsize=10)
        fig.suptitle('Partition Comparison Grid (Small Partitions)', fontsize=16, y=0.995)
        plt.tight_layout()
        plt.show()

    # ==========================
    # LARGE PARTITIONS IN SEPARATE WINDOWS
    # ==========================
    for key in large_keys:
        values_a, values_b = dict_a[key], dict_b[key]
        if len(values_a) != len(values_b):
            raise ValueError(f"Value lists for key '{key}' must have same length")

        fig, ax = plt.subplots(figsize=(12, 5))
        x = np.arange(len(values_a))
        width = 0.4
        ax.bar(x - width/2, values_a, width, label=title_a, color='skyblue')
        ax.bar(x + width/2, values_b, width, label=title_b, color='salmon')
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
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print(
            "Usage: python script.py <graph_file>"
        )
        sys.exit(1)
    
    graph_filename = sys.argv[1]    

    find_files(graph_filename)