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

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python script.py <graph_file> <type>"
        )
        sys.exit(1)
    
    graph_filename = sys.argv[1]
    type = sys.argv[2]
    
    if (type != "rg-mk" and type != "cut"):
        print("Wrong type!")
        sys.exit(1)

    form_stats(graph_filename, type)