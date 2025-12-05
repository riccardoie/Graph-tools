import csv
from collections import defaultdict

def translate():
    # Step 1: Read edges
    edges = set()
    nodes_set = set()

    with open("roadNet-CA.txt", newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if("#" in row[0]):
                continue
            tmp = row[0].split()
            a, b = int(tmp[0]), int(tmp[1])
            # 0-index → 1-index
            a += 1
            b += 1
            edges.add(tuple(sorted((a, b))))
            nodes_set.update([a, b])

    # Step 2: Build adjacency
    N = max(nodes_set)  # total nodes
    adj = [[] for _ in range(N)]
    for a, b in edges:
        adj[a-1].append(b)
        adj[b-1].append(a)

    # Step 3: Write METIS file
    with open("../graphs/roadsCA_graph", "w") as f:
        f.write(f"{N} {len(edges)}\n")
        for neighbors in adj:
            f.write(" ".join(map(str, sorted(neighbors))) + "\n")

translate()