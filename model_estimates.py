import matplotlib.pyplot as plt
import argparse
import numpy as np

BW_MP = [1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1]

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
                incoming_msgs[p][1][partition] += 1 # times 8 bytes
                incoming_msgs[partition][0].add(p)
    return incoming_msgs

def calculate_time(graph, version, nr_of_partitions, startup_latency):
    N = nr_of_partitions
    incoming_msg = calculate_incoming_msg(graph, version, N)

    # Precompute V_i (volume sums) once
    V = [sum(incoming_msg[i][1]) for i in range(N)]

    # Sort values after V, keep same order for incoming msgs
    order = sorted(range(N), key=lambda i: V[i])
    V = [V[i] for i in order]
    incoming_msg = [incoming_msg[i] for i in order]

    # Precompute trecv for all i iteratively
    trecv_vals = [0.0] * N
    trecv_vals[0] = N * V[0] / BW_MP[N - 1]
    for i in range(1, N):
        delta_V = V[i] - V[i - 1]
        trecv_vals[i] = (N - i) * delta_V / BW_MP[N - i] + trecv_vals[i - 1]

    # Compute tsend for all (i, j) iteratively
    times = []
    for i in range(N):
        M_in = len(incoming_msg[i][0])
        s = incoming_msg[i][1]
        trecv_i = trecv_vals[i]

        max_msg = trecv_i  # baseline from trecv
        tsend_ij = M_in * s[0] / V[i] * trecv_i if V[i] > 0 else 0
        max_msg = max(max_msg, tsend_ij)

        # UNTIL M_IN
        for j in range(1, M_in):
            delta_s = s[j] - s[j - 1]
            tsend_ij = (M_in - j) * delta_s / V[i] * trecv_i + tsend_ij if V[i] > 0 else 0
            max_msg = max(max_msg, tsend_ij)

        times.append(M_in * startup_latency + max_msg)

    return times


def model_estimate(graph, type, nr_of_partitions, startup_latency):
    times_metis = calculate_time(graph, "vol_partitions", nr_of_partitions, startup_latency)
    # times_nvol22 = calculate_time(graph, "nvol_03", nr_of_partitions, startup_latency, bandwidth)
    times_nvol = calculate_time(graph, type, nr_of_partitions, startup_latency)
    
    max_metis = max(times_metis)
    max_nvol = max(times_nvol)
    # max_nvol22 = max(times_nvol22)

    x = np.arange(len(times_metis))
    width = 0.35

    plt.bar(x - width/2, times_metis, width, label="METIS (baseline)")
    plt.bar(x + width/2, times_nvol, width, label=f"NVOL ({(max_nvol - max_metis) / max_metis * 100:+.1f}%)")

    # Optional labels
    plt.xlabel("partition")
    plt.ylabel("Time")
    plt.title("Time difference")
    plt.legend()
    # Show plot
    plt.show()


def parse_bandwidth(value):
    try:
        return list(map(int, value.split(",")))
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Bandwidth must be a comma-separated list of integers (e.g. 10,20,30)"
        )

# if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run model estimation")

    parser.add_argument("graph_file", help="Name of graph file")
    parser.add_argument("type", help="Type of model")
    parser.add_argument("nr_of_partitions", type=int, help="Number of partitions")
    parser.add_argument("startup_latency", type=float, help="Startup latency")
    # parser.add_argument("bandwidth", type=float, help="Startup latency")

    parser.add_argument(
        "--bandwidth",
        required=True,
        type=parse_bandwidth,
        help="Comma-separated bandwidth values (e.g. 10,20,30)",
    )

    args = parser.parse_args()

    # Validate bandwidth length
    if len(args.bandwidth) != args.nr_of_partitions:
        parser.error(
            "Number of bandwidth values must match nr_of_partitions"
        )

    model_estimate(
        args.graph_file,
        args.type,
        args.nr_of_partitions,
        args.startup_latency,
        args.bandwidth,
    )

model_estimate("heart03_graph", "nvol_02", 32, 1)