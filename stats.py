import sys 

def form_stats(filename, size):
    #Partition file
    partition_file = open(f"{filename}.part.{size}")
    content = partition_file.readlines()

    partitions = [0] * int(size)

    #Original graph file 
    with open(f"{filename}") as graph_file:
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

    for pid, cut in enumerate(partitions):
        print(f"Pid {pid} has cut: {cut}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python script.py <graph_file> <num_parts>"
        )
        sys.exit(1)
    
    graph_filename = sys.argv[1]
    num_parts = sys.argv[2]
    form_stats(f"../graphs/{graph_filename}", num_parts)
