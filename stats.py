import sys 
import os

#Finds the cut per partition

def form_stats(filename, type):
    #Partition file
    
    results = {}
    source_folder = "../rg-mk_partitions" if type == "rg-mk" else "../cut_partitions"
    for partition_file in os.listdir(source_folder):
        if filename in partition_file:

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

    with open(f"output_stats/{type}_{filename}_partitions", "w") as output:
        for key, value in results.items(): 
            output.write(f"{key}\n")
            for pid, cut in enumerate(value):
                  output.write(f"\tPid {pid}: {cut}\n")
            output.write("\n")

def form_volstats(filename, type):
    #Partition file
    
    results = {}
    source_folder = "../nvol_partitions"
    for partition_file in os.listdir(source_folder):
        if filename in partition_file:

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

    # Write output
    with open(f"output_stats/{type}_{filename}_partitions", "w") as output:
        for key, value in results.items(): 
            output.write(f"{key}\n")
            for pid, vol in enumerate(value):
                output.write(f"\tPid {pid}: {vol}\n")
            output.write("\n")



# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print(
#             "Usage: python script.py <graph_file> <type>"
#         )
#         sys.exit(1)
    
#     graph_filename = sys.argv[1]
#     type = sys.argv[2]
    
#     if(type == "nvol"):
#         form_volstats(graph_filename, type)

#     elif (type == "rg-mk" or type == "cut"):
#         form_stats(graph_filename, type)

#     else:
#         print("Wrong type!")
#         sys.exit(1)

files_grid = ["4_graph", "10_graph", "15_graph", "20_graph", "100_graph", "1000_graph"]
files_cube = ["3_cube_graph", "5_cube_graph", "10_cube_graph", "100_cube_graph"]

for file in files_grid:
    form_stats(file, "cut")
    form_stats(file, "rg-mk")
    print("Finished" + file)
for file in files_cube:
    form_stats(file, "rg-mk")
    form_stats(file, "cut")
    print("Finished" + file)

form_stats("deezer_graph", "cut")
form_stats("skitter_graph", "cut")
form_stats("deezer_graph", "rg-mk")
form_stats("skitter_graph", "rg-mk")
form_stats("roadsCA_graph", "rg-mk")
form_stats("roadsCA_graph", "cut")