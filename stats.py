import os 


def form_stats(filename, size):

    #Partition file
    partition_file = open(f"../{filename}.part.{size}")
    content = partition_file.readlines()

    partitions = [0] * size

    #Original graph file 
    with open(f"../{filename}") as graph_file:
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

    for n in partitions:
        print(n)

form_stats("100_graph", 7)