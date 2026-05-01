import subprocess
import os
import shutil

#Given a graph file stored in a folder graphs with the relative path ../graphs This script will 
#run metis with the described type (cut or rg-mk). The output will be parsed and stored in a txt
#file in a specific folder, and the partition file will also be saved in a specific folder 
#based on the type of partition performed. 
#The script will over an array so several files can be passed at once. For now the number of 
#partitions is capped to the array partitions below, might change this later. 

files_grid = ["4_graph", "10_graph", "15_graph", "20_graph", "100_graph", "1000_graph"]
files_cube = ["3_cube_graph", "5_cube_graph", "10_cube_graph", "100_cube_graph"]
files_heart = ["heart01_graph", "heart02_graph", "heart03_graph", "heart04_graph", "heart05_graph","heart06_graph"]
# glisne_matrixes = ["fe_tooth_graph", "roadNet-CA_graph","channel-500x100x100-b050_graph", "hugetric-00000_graph", "hugetric-00020_graph", "hugetrace-00020_graph","kmer_U1a_graph", "kmer_V2a_graph"]
glisne_matrixes = ["fe_tooth_graph", "roadNet-CA_graph","channel-500x100x100-b050_graph", "hugetric-00000_graph", "hugetric-00020_graph",]

# glisne_matrixes = ["Spielman_k400_graph"]
# glisne_matrixes = ["kmer_U1a_graph"]
# glisne_matrixes = ["fe_tooth_graph"]
# glisne_matrixes = ["citationCiteseer_graph"]
# glisne_matrixes = ["hugetric-00000_graph", "hugetric-00020_graph"]

partitions = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
# partitions = [2, 4, 8, 16, 32]


def run_metis(type, files, folder):
    path = f"../{folder}"
    os.makedirs(path, exist_ok=True)
    os.makedirs(f"{path}/stats", exist_ok=True)
    for file in files: 
        with open(f"../graphs/{file}", 'r') as tmp:
            first_line = tmp.readline().strip().split() # Read the first line and remove whitespace
        
        print(str(file))
        n = int(first_line[0])

        for partition in partitions:

            if(not n >= partition * partition):
                break

            if type == "rg-mk":
                command = ["gpmetis", f"../graphs/{file}", str(partition), "-objtype=rg-mk"]
                result = subprocess.run(command, capture_output=True, text=True)
                parse_result(result, folder, f"{file}_{str(partition)}_stats")
                # parse_iterations(result, "rg-mk_partitions", f"{file}_{str(partition)}_stats")
            elif type == "cut":
                command = ["gpmetis", f"../graphs/{file}", str(partition)]
                result = subprocess.run(command, capture_output=True, text=True)
                parse_result(result, folder, f"{file}_{str(partition)}_stats")
                # parse_iterations(result, "cut_partitions", f"{file}_{str(partition)}_stats")
            elif type == "nvol":
                command = ["gpmetis", f"../graphs/{file}", str(partition), "-objtype=nvol"]
                result = subprocess.run(command, capture_output=True, text=True)
                parse_result(result, folder, f"{file}_{str(partition)}_stats")
            elif type == "vol":
                command = ["gpmetis", f"../graphs/{file}", str(partition), "-objtype=vol"]
                result = subprocess.run(command, capture_output=True, text=True)
                parse_result(result, folder, f"{file}_{str(partition)}_stats")
            else:
                print("WRONG TYPE")

        print(f"Finished {file}")

    move_files(folder)
        
def parse_iterations(output, destination, file):
    
    for line in output.stdout.splitlines():
        if "Metis had" in line and "iterations" in line:
            end_ind = line.find("iterations")
            start_ind = len("Metis had")
            iterations = line[start_ind:end_ind]

            print(iterations)

def move_files(destination):

    # --- Configuration ---
    source_folder = "../graphs"
    destination_folder = f"../{destination}"

    # Make sure the destination exists
    os.makedirs(destination_folder, exist_ok=True)

    # Loop through all files in source
    for filename in os.listdir(source_folder):
        if ".part" in filename:
            src_path = os.path.join(source_folder, filename)
            dst_path = os.path.join(destination_folder, filename)

            # Only move if it's a file
            if os.path.isfile(src_path):
                shutil.move(src_path, dst_path)
                print(f"Moved: {filename}")

    print("✅ Done moving all '.part' files.")

def parse_result(output, destination, file): 

    ed = cv = balance = io_time = pt_time = rep_time = None
    overweight = None
    connectivity = None
    contiguous = None

    for line in output.stdout.splitlines():

        if "Edgecut:" in line and "communication volume" in line:
            ed_ind = line.lower().find("edgecut:") + len("edgecut:")
            cv_ind = line.lower().find("communication volume:") + len("communication volume:")
            ed = line[ed_ind:line.find(",")].strip()
            cv = line[cv_ind:line.find(".")].strip()

        elif "constraint #0:" in line:
            balance = line[line.find("constraint #0:") + len("constraint #0:"):].strip()

        elif "Most overweight partition:" in line:
            continue

        elif "pid:" in line and "actual:" in line:
            overweight = line.strip()

        elif "Subdomain connectivity:" in line:
            connectivity = line.split("Subdomain connectivity:")[-1].strip()

        elif "Each partition is contiguous" in line:
            contiguous = "Yes"
        
        elif "There are" in line and "non-contiguous partitions." in line:
            contiguous = line.split("There are")[1].split("non-contiguous")[0].strip()
        elif "I/O:" in line:
            io_time = line[line.find("I/O:") + len("I/O:"):].strip()

        elif "Partitioning:" in line:
            pt_time = line[line.find("Partitioning:") + len("Partitioning:"): line.find("(")].strip()

        elif "Reporting:" in line:
            rep_time = line[line.find("Reporting:") + len("Reporting:"):].strip()

    write_metrics_to_file(
        f"../{destination}/stats/{file}.txt",
        ed, cv, balance, io_time, pt_time, rep_time,
        overweight, connectivity, contiguous
    )

def write_metrics_to_file(path, ed, cv, balance, io_time, pt_time, rep_time,
                          overweight=None, connectivity=None, contiguous=None):

    with open(path, "w") as f:
        f.write("=== Partitioning Results ===\n")

        if ed:
            f.write(f"Edgecut:                 {ed}\n")

        if cv:
            f.write(f"Communication Volume:    {cv}\n")

        if balance:
            f.write(f"Balance:                 {balance}\n")

        if overweight:
            f.write(f"Most Overweight Part.:   {overweight}\n")

        if connectivity:
            f.write(f"Subdomain Connectivity:  {connectivity}\n")

        if contiguous:
            f.write(f"Contiguous Partitions:   {contiguous}\n")

        if io_time:
            f.write(f"I/O Time:                {io_time}\n")

        if pt_time:
            f.write(f"Partition Time:          {pt_time}\n")

        if rep_time:
            f.write(f"Reporting Time:          {rep_time}\n")


# folder = "cut_partitions"
# type = "cut"
# run_metis(type, glisne_matrixes, folder)
# print("Finished nvol contig")
# # run_metis(type, ["skitter_graph"], folder)
# # run_metis(type, ["deezer_graph"], folder)
# # run_metis(type, ["roadsCA_graph"], folder)


# # # run_metis(type, ['Spielman_k400_graph'], folder)
# run_metis(type, glisne_matrixes, folder)
# run_metis(type, files_cube, folder)
# run_metis(type, files_grid, folder)
# run_metis(type, files_heart, folder)
# run_metis(type, ['Spielman_k400_graph'], folder)