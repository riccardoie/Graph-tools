import matplotlib.pyplot as plt
import sys


def calculate_incoming_msg(graph, version, N):

    # For each partition it stores {set of reachable partitions} [array of size partitions, with the incoming messages from a given partiton]
    incoming_msgs = [(set(), [0] * N) for _ in range(N)]

    source_folder =f"../{version}"

    # Open partition file
    with open(f"{source_folder}/{graph}.part.{N}") as file:
        content = file.readlines()

    # Original graph file 
    with open(f"../graphs/{graph}") as graph_file:
        for i, line in enumerate(graph_file):
            
            # Skip header
            if i == 0:
                continue

            # Get neighboring nodes of i
            # If we have node size it needs changes here
            neighbors = list(map(int, line.strip().split()))

            partition = int(content[i - 1])  # Current partition of i, 0-based index
            neighbor_partitions = set()

            # For each neighbor vertex store which partition they belong to
            for nbr in neighbors:
                n_p = int(content[nbr - 1])  # Partition of neighbor node
                
                # If its different from i's partition add to set
                if n_p != partition:
                    neighbor_partitions.add(n_p)
            # For each partition k neighbor to i, add one to incoming messages to partition k
            # Store the set of reachable partitions for i's partition
            for p in neighbor_partitions:
                incoming_msgs[p][1][partition] += 1
                incoming_msgs[partition][0].add(p)
    return incoming_msgs

def calculate_time(graph, version, nr_of_partitions, startup_latency, BW_MP):
    N = nr_of_partitions
    incoming_msg = calculate_incoming_msg(graph, version, N)

    # Precompute V_i (volume sums) once
    V = [sum(incoming_msg[i][1]) for i in range(N)]

    # Precompute trecv for all i iteratively
    trecv_vals = [0.0] * N
    trecv_vals[0] = N * V[0] / BW_MP
    for i in range(1, N):
        delta_V = V[i] - V[i - 1]
        trecv_vals[i] = (N - i) * delta_V / BW_MP + trecv_vals[i - 1]

    # Compute tsend for all (i, j) iteratively
    times = []
    for i in range(N):
        M_in = len(incoming_msg[i][0])
        s = incoming_msg[i][1]
        trecv_i = trecv_vals[i]

        max_msg = trecv_i  # baseline from trecv
        tsend_ij = M_in * s[0] / V[i] * trecv_i if V[i] > 0 else 0
        max_msg = max(max_msg, tsend_ij)

        for j in range(1, N):
            delta_s = s[j] - s[j - 1]
            tsend_ij = (M_in - j) * delta_s / V[i] * trecv_i + tsend_ij if V[i] > 0 else 0
            max_msg = max(max_msg, tsend_ij)

        times.append(M_in * startup_latency + max_msg)

    return times


def model_estimate(graph, type, nr_of_partitions, startup_latency, bandwidth):
    times_metis = calculate_time(graph, "vol_partitions", nr_of_partitions, startup_latency, bandwidth)
    times_nvol = calculate_time(graph, type, nr_of_partitions, startup_latency, bandwidth)


    plt.plot(times_metis, label="METIS")
    plt.plot(times_nvol, label="NVOL")

    # Optional labels
    plt.xlabel("partition")
    plt.ylabel("times")
    plt.title("Time difference")
    plt.legend()
    # Show plot
    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: python script.py <graph_file> <type> <nr of partitions> <startup_latency> <bandwidth>"
        )
        sys.exit(1)
    
    graph_filename = sys.argv[1]
    type = sys.argv[2]
    nr_of_partitions = int(sys.argv[3])
    startup_latency = int(sys.argv[4])
    bandwidth = int(sys.argv[5])

    model_estimate(graph_filename, type, nr_of_partitions, startup_latency, bandwidth)