import matplotlib.pyplot as plt
import argparse
import numpy as np
import re
bandwith = [5,     #1
        10.5,   #2
        0.5*(10.5 + 14.8),
        14.8,   #4
        0.5*(16.7 + 14.8),
        16.7,   #6
        0.5*(16.7 + 17.0),
        17.0,   #8
        0.5*(17.0 + 18.8),
        18.8,   #10
        0.5*(18.8 + 19.5),
        19.5,   #12
        0.5*(19.5 + 19.5),
        19.5,   #14
        0.5*(19.5 + 19.8),
        19.8,   #16
        0.5*(19.8 + 22.5),
        22.5,   #18
        0.5*(22.3 + 25.3),
        25.3,   #20
        0.5*(25.3 + 25.3),
        25.3,   #22
        0.5*(25.3 + 26.1),
        26.1,   #24
        0.5*(26.1 + 26.1),
        26.1,   #26
        0.5*(26.1 + 26.1),
        26.1,   #28
        0.5*(26.1 + 26.1),
        26.1,   #30
        0.5*(26.1 + 26.9),
        26.9]   #32

BW_MP = [x * 1024*1024*1024 for x in bandwith]


tau = 3.8 * 10**-6

def calculate_incoming_msg(graph, version, N):

    # For each partition it stores {set of reachable partitions} [array of size partitions, with the incoming messages from a given partiton]
    incoming_msgs = [(set(), [0] * N) for _ in range(N)]

    source_folder =f"../{version}"
    # print(source_folder)
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
                incoming_msgs[p][1][partition] +=  8 #8 bytes
                incoming_msgs[partition][0].add(p)
    return incoming_msgs

def retrieve_incoming_msg(graph, version, N):

    path = f"output_stats/{version}_partitions/incoming_vol/{version}_{graph}_partitions"

    target_suffix = f".part.{N}"
    in_section = False
    pid_data = {}
    PID_LINE = re.compile(r"Pid\s+(\d+)\s+Vol:\s+(\d+)\s+Neighbors:\s+(\d+)")

    with open(path) as f:
        for raw in f:
            line = raw.rstrip("\n")

            if not line.strip():
                # Blank line ends the current section.
                if in_section:
                    break
                continue

            if not raw.startswith("\t"):
                # Header line, e.g. "graph.part.4"
                in_section = line.strip().endswith(target_suffix)
                continue

            if in_section:
                m = PID_LINE.search(line)
                if m:
                    pid_data[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))

    return [pid_data[i] for i in sorted(pid_data)]


def calculate_time(graph, version, nr_of_partitions, startup_latency):
    N = nr_of_partitions
    incoming_msg = calculate_incoming_msg(graph, version, N)

    # Precompute V_i (volume sums) once
    V = [sum(incoming_msg[i][1]) for i in range(N)]

    # for n, val in enumerate(V):
    #     print(f"Partition {n}, num nabo:{len(incoming_msg[n][0])}, incoming volume: {val/8}")

    # Sort values after V, keep same order for incoming msgs
    order = sorted(range(N), key=lambda i: V[i])
    V = [V[i] for i in order]
    # if ("nvol" in version):
        # print(V)
    incoming_msg = [incoming_msg[i] for i in order]

    # Precompute trecv for all i iteratively
    trecv_vals = [0.0] * N
    trecv_vals[0] = N * V[0] / BW_MP[N - 1]

    for i in range(1, N):
        delta_V = V[i] - V[i - 1]
        trecv_vals[i] = ((N - i) * delta_V / BW_MP[N - 1 - i])+ trecv_vals[i - 1]

    # print(trecv_vals)
    # print(order)

    # Compute tsend for all (i, j) iteratively
    tsend = [0] * N

    for i in range(N):
        M_in = len(incoming_msg[i][0])
        neighbor_pids = incoming_msg[i][0]
        volumes = incoming_msg[i][1]
        neighbor_pids = sorted(neighbor_pids, key=lambda p: volumes[p])
        s = [volumes[p] for p in neighbor_pids] 

        # print(s)
        trecv_i = trecv_vals[i]

        tsend_ij = M_in * s[0] / V[i] * trecv_i
        if (tsend[neighbor_pids[0]] < tsend_ij):
            tsend[neighbor_pids[0]] = tsend_ij
        
        # UNTIL M_IN
        for j in range(1, M_in):
            delta_s = s[j] - s[j - 1]
            tsend_ij = (M_in - j) * delta_s / V[i] * trecv_i + tsend_ij

            if(tsend[neighbor_pids[j]] < tsend_ij):
                tsend[neighbor_pids[j]] = tsend_ij

    # print(tsend)
    # print(trecv_vals)
    times = []
    maxmax = 0

    for i in range(N):
        M_in = len(incoming_msg[i][0])
        max_msg = max(trecv_vals[i], tsend[order[i]])

        # if (max_msg > maxmax):
        #     maxmax = max_msg    

        times.append(M_in * startup_latency + max_msg)
        # times.append(max_msg)

    # print(maxmax)
    # Reorder back to partition-id order
    times_by_pid = [0.0] * N
    for k, pid in enumerate(order):
        times_by_pid[pid] = times[k]

    return times_by_pid


def model_estimate(graph, type, nr_of_partitions, startup_latency):
    times_metis = calculate_time(graph, "vol_partitions", nr_of_partitions, startup_latency)
    times_nvol = calculate_time(graph, type, nr_of_partitions, startup_latency)
    times_nvol4 = calculate_time(graph, f"{type}_4", nr_of_partitions, startup_latency)

    # print(times_metis)
    # for n, val in enumerate(times_nvol):
    #     print(f"Partition {n}, pure recv time: {val}")

    max_metis = max(times_metis)
    max_nvol = max(times_nvol)
    max_nvol4 = max(times_nvol4)

    rnvol = ((max_metis - max_nvol) / max_metis * 100)
    rnvol4 = ((max_metis- max_nvol4) / max_metis * 100)

    print(rf"{graph} & ${max_metis:.2e}$ & ${max_nvol:.2e}$ & ${max_nvol4:.2e}$ & ${rnvol:.2f}\%$ & ${rnvol4:.2f}\%$\\")
    print(r"\hline")
    # print((max_nvol - max_metis) / max_metis * 100)

    # x = np.arange(len(times_metis))
    # width = 0.35
    # plt.figure(figsize=(12, 5))
    # # ax = plt.axes()
    # # ax.set_position([0.15, 0.15, 0.75, 0.75])
    # plt.bar(x - width/2, times_metis, width, label="VOL 3%", color="#000000")
    # plt.bar(x + width/2, times_nvol, width, label=f"NVOL 4%", color="#E65A0F")

    # # Optional labels
    # plt.xlabel("Process")
    # plt.ylabel("Estimated communication time in seconds")
    # plt.title(f"Communication times estimates {graph} k={nr_of_partitions} (No latency)")
    # plt.legend()
    # # Show plot
    # plt.show()


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

# channel-500x100x100-b050_graph
# hugetrace-00020_graph
# heart06_graph
# roadNet-CA_graph
# citationCiteseer_graph
# kmer_U1a_graph

# model_estimate("heart01_graph", "nvol_08", 32, tau)
# model_estimate("heart06_graph", "nvol_08", 32, tau)
# model_estimate("kmer_U1a_graph", "nvol_08", 32, tau)
files_heart = ["hugetric-00020_graph", "rgg_n_2_23_s0_graph", "delaunay_n23_graph", "hugetrace-00020_graph", "delaunay_n24_graph", "kmer_V2a_graph", "kmer_U1a_graph"]
for n in files_heart:
    model_estimate(n, "nvol_08", 32, tau)