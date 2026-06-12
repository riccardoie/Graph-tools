import os

def translate(file):
    edges = set()

    with open(file, newline='') as f:
        # Skip comment lines
        for line in f:
            if not line.startswith('%'):
                break
        
        # Parse header
        header = line.split()
        nr_of_vertices = int(header[0])

        # Parse edges
        for line in f:
            tmp = line.split()
            if len(tmp) < 2:
                continue
            a, b = int(tmp[0]), int(tmp[1])
            if a == b:
                continue
            edges.add(tuple(sorted((a, b))))

    print(f"Vertices: {nr_of_vertices}, Unique edges: {len(edges)}")

    # Build adjacency list (0-indexed internally)
    adj = [[] for _ in range(nr_of_vertices)]
    for a, b in edges:
        adj[a - 1].append(b)
        adj[b - 1].append(a)

    # Write METIS file
    os.makedirs("../graphs", exist_ok=True)
    with open(f"../graphs/{file}_graph", "w") as f:
        f.write(f"{nr_of_vertices} {len(edges)}\n")
        for neighbors in adj:
            f.write(" ".join(map(str, sorted(neighbors))) + "\n")

# translate("delaunay_n23")
# translate("packing-500x100x100-b050")