import sys 
import os

#Finds the cut per partition
def form_stats(filename, folder, filter):
    #Partition file
    
    source_folder =f"../{filter}/{folder}"

    if(folder == "cut"):
        source_folder = f"../{folder}_partitions"

    results = {}
    # source_folder = "../rg-mk_partitions_new_version" if type == "rg-mk" else "../cut_partitions"
    for partition_file in os.listdir(source_folder):
        if partition_file.startswith(filename):

            file = open(f"{source_folder}/{partition_file}")

            size = (partition_file[partition_file.find("part.") + 5 :])

            content = file.readlines()

            partitions = [0] * int(size)

            #Original graph file 
            with open(f"../graphs/{filename}") as graph_file:
                for i, line in enumerate(graph_file):

                    #Store header info
                    if(i == 0):
                        header = line.strip().split()
                        nr_of_nodes = header[0]
                        continue
                    
                    #Get the partition of node i
                    partition = int(content[i - 1])
                    neighbors = line.strip().split()            

                    #Check if the neighbors of i are in the same partition
                    for n in neighbors:
                        n_p = int(content[int(n) - 1])

                        if (partition != n_p):
                            partitions[partition] += 1
        
            results[partition_file] = partitions

    os.makedirs(f"output_stats/{filter}/{folder}_partitions", exist_ok=True)
    with open(f"output_stats/{filter}/{folder}_partitions/{folder}_{filename}_partitions", "w") as output:
        for key, value in results.items(): 
            output.write(f"{key}\n")
            for pid, cut in enumerate(value):
                  output.write(f"\tPid {pid}: {cut}\n")
            output.write("\n")

def form_volstats(filename, folder):
    #Partition file

    source_folder = f"../{folder}"

    if ("nvol" not in folder and "contig" not in folder):
        source_folder = f"../{folder}_partitions"

    results = {}

    for partition_file in os.listdir(source_folder):

        graph_name = partition_file[:partition_file.find(".")]
        if filename == graph_name:          
            # Open the partition file
            file = open(f"{source_folder}/{partition_file}")

            # Extract partition count from filename (e.g., graph.part.4)
            size = (partition_file[partition_file.find("part.") + 5:])
            content = file.readlines()

            # Initialize volume count for each partition
            partitions = [0] * int(size)

            # Track neighbors per vertex for volume computation
            node_neighbors = {}

            # Original graph file 
            with open(f"../graphs/{filename}") as graph_file:
                for i, line in enumerate(graph_file):
                    
                    # Store header info
                    if i == 0:
                        header = line.strip().split()
                        nr_of_nodes = int(header[0])
                        continue
                    
                    # Graph line, get neighboring nodes
                    neighbors = list(map(int, line.strip().split()))
                    node_neighbors[i - 1] = neighbors  # Store 0-based index

            # Compute communication volume
            for node, neighbors in node_neighbors.items():
                partition = int(content[node])  # Current partition of the node
                neighbor_partitions = set()

                for n in neighbors:
                    n_p = int(content[n - 1])  # Partition of neighbor node
                    if n_p != partition:
                        neighbor_partitions.add(n_p)

                # Add one (or more if weighted) volume for each unique external partition
                partitions[partition] += len(neighbor_partitions)

            # Store results
            results[partition_file] = partitions

    # # Write output
    if(folder == "vol"):
        os.makedirs(f"output_stats/{folder}_partitions", exist_ok=True)
        with open(f"output_stats/{folder}_partitions/{folder}_partitions_{filename}_volpartitions", "w") as output:
            for key, value in results.items(): 
                output.write(f"{key}\n")
                for pid, vol in enumerate(value):
                    output.write(f"\tPid {pid} Vol: {vol}\n")
                output.write("\n")

    else:
        os.makedirs(f"output_stats/{folder}_partitions", exist_ok=True)
        with open(f"output_stats/{folder}_partitions/{folder}_{filename}_partitions", "w") as output:
            for key, value in results.items(): 
                output.write(f"{key}\n")
                for pid, vol in enumerate(value):
                    output.write(f"\tPid {pid} Vol: {vol}\n")
                output.write("\n")
