import networkx as nx
import sys

def write_metis_format(G, filename, fmt="000"):
    """Writes a NetworkX graph to METIS format."""
    mapping = {node: i + 1 for i, node in enumerate(G.nodes())}
    H = nx.relabel_nodes(G, mapping)
    n = H.number_of_nodes()
    m = H.number_of_edges()

    with open(filename, "w") as f:
        f.write(f"{n} {m} {fmt}\n")
        for i in range(1, n + 1):
            neighbors = sorted(list(H.neighbors(i)))
            line = " ".join(str(neighbor) for neighbor in neighbors)
            f.write(line + "\n")

    print(f"Graph written to {filename} in METIS format.")


def generate_graph(graph_type, filename, *args):
    """Generates a graph based on type and writes to METIS."""
    if graph_type == "grid":
        size = int(args[0]) if args else 10
        G = nx.grid_2d_graph(size, size)
    elif graph_type == "3d":
        size = int(args[0]) if args else 5
        G = nx.grid_graph((size, size, size))
    else:
        print(f"Unknown graph type: {graph_type}")
        return

    write_metis_format(G, filename)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python script.py <graph_type> <output_file> [optional parameters]"
        )
        print("Example (grid 10x10): python script.py grid grid.metis 10")
        sys.exit(1)

    graph_type = sys.argv[1]
    filename = sys.argv[2]
    params = sys.argv[3:]

    generate_graph(graph_type, f"../graphs/{filename}", *params)
