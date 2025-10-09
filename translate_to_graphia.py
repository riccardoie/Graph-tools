# metis_to_graphia.py
# Converts a METIS graph and partition file into a Graphia-ready edge list with node partitions

def metis_to_graphia(graph_file, part_file, output_file):
    # Read partitions
    with open(part_file) as f:
        partitions = [line.strip() for line in f if line.strip()]

    # Read graph edges and convert to edge list
    edges = set()
    with open(graph_file) as f:
        first_line = f.readline()
        n, m, type = first_line.strip().split()
        for i, line in enumerate(f, start=1):
            neighbors = map(int, line.split())
            for j in neighbors:
                if i < j:  # avoid duplicates
                    edges.add((i, j))

    # Write Graphia-ready TSV: source, target, source_partition
    with open(output_file, "w") as f:
        f.write("Source\tTarget\tPartition\n")
        for u, v in sorted(edges):
            partition = partitions[u - 1]  # METIS nodes are 1-based
            f.write(f"{u}\t{v}\t{partition}\n")

    print(f"Graphia-ready file saved as: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert METIS graph + partition to Graphia-ready TSV")
    parser.add_argument("graph_file", help="METIS graph file (.graph)")
    parser.add_argument("part_file", help="METIS partition file (.part.*)")
    parser.add_argument("output_file", help="Output TSV file for Graphia")
    args = parser.parse_args()

    metis_to_graphia(args.graph_file, args.part_file, args.output_file)
