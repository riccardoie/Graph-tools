# Graph-tools
create_graph.py forms a graph in metis format
    Usage: python script.py <graph_type> <output_file> [optional parameters]

    Where graph type is either grid or cube. Optional parameters is the size of the graph, default is 10
    Grid will be 10x10
    Cube will be 10x10x10

run_metis.py will run metis and store the partition file, and the output from the terminal in each their file. It takes an array of graph files as input. 
    
    Usage: To be updated, run_metis("type","file_array")
    Where graph type is either cut or rg-mk.

stats.py takes a graph file and computes all the partition sizes for all existing partition files on that graph.

    Usage: python script.py <graph_file> <type>
    Where graph type is either cut or rg-mk.

graph_results.py will output the file generetad by stats.py in a bar chart. Given a specific graph it will find the rg-mk and cut version and compare them in the barchart. 