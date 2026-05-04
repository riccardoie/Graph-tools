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

    # if ("nvol" not in folder and "contig" not in folder):
    #     source_folder = f"../{folder}_partitions"
    results = {}
    # Original graph file 
    with open(f"../graphs/{filename}") as graph_file:
        next(graph_file)
        adjacency = [list(map(int, line.split())) for line in graph_file]

    for partition_file in os.listdir(source_folder):
        graph_name = partition_file[:partition_file.find(".")]
        
        # Different graph skip to next
        if filename != graph_name:
            continue
        
        # Read the partition assignments once
        with open(f"{source_folder}/{partition_file}") as file:
            size = int(partition_file[partition_file.find("part.") + 5:])
            part_of = [int(x) for x in file]

        # Compute outgoing communication volume per partition
        partitions = [0] * size
        for i, neighbors in enumerate(adjacency):
            p = part_of[i]
            external = {part_of[n - 1] for n in neighbors if part_of[n - 1] != p}
            partitions[p] += len(external)

        results[partition_file] = partitions

    # Write output
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

def incoming_volstats(filename, folder):
        #Partition file
    source_folder = f"../{folder}"

    # if ("nvol" not in folder and "contig" not in folder):
    #     source_folder = f"../{folder}_partitions"
    results = {}
    # Original graph file 
    with open(f"../graphs/{filename}") as graph_file:
        next(graph_file)
        adjacency = [list(map(int, line.split())) for line in graph_file]

    for partition_file in os.listdir(source_folder):
        graph_name = partition_file[:partition_file.find(".")]
        
        # Different graph skip to next
        if filename != graph_name:
            continue
        
        # Read the partition assignments once
        with open(f"{source_folder}/{partition_file}") as file:
            size = int(partition_file[partition_file.find("part.") + 5:])
            part_of = [int(x) for x in file]

        # Compute incoming communication volume per partition
        partitions = [0] * size
        for i, neighbors in enumerate(adjacency):
            p = part_of[i]
            external = {part_of[n - 1] for n in neighbors if part_of[n - 1] != p}
            for ext_p in external:
                partitions[ext_p] += 1

        results[partition_file] = partitions

    # Write output
    if(folder == "vol"):
        os.makedirs(f"output_stats/{folder}_partitions/incoming_vol", exist_ok=True)
        with open(f"output_stats/{folder}_partitions/incoming_vol/{folder}_partitions_{filename}_volpartitions", "w") as output:
            for key, value in results.items(): 
                output.write(f"{key}\n")
                for pid, vol in enumerate(value):
                    output.write(f"\tPid {pid} Vol: {vol}\n")
                output.write("\n")

    else:
        os.makedirs(f"output_stats/{folder}_partitions/incoming_vol/", exist_ok=True)
        with open(f"output_stats/{folder}_partitions/incoming_vol/{folder}_{filename}_partitions", "w") as output:
            for key, value in results.items(): 
                output.write(f"{key}\n")
                for pid, vol in enumerate(value):
                    output.write(f"\tPid {pid} Vol: {vol}\n")
                output.write("\n")