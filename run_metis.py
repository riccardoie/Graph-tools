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
partitions = [4, 5, 10, 15, 25, 50, 100]



def run_metis(type, files):
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
                parse_result(result, "rg-mk_partitions", f"{file}_{str(partition)}_stats")
                # parse_iterations(result, "rg-mk_partitions", f"{file}_{str(partition)}_stats")
            elif type == "cut":
                command = ["gpmetis", f"../graphs/{file}", str(partition)]
                result = subprocess.run(command, capture_output=True, text=True)
                parse_result(result, "cut_partitions", f"{file}_{str(partition)}_stats")
                # parse_iterations(result, "cut_partitions", f"{file}_{str(partition)}_stats")
            elif type == "nvol":
                command = ["gpmetis", f"../graphs/{file}", str(partition), "-objtype=nvol"]
                result = subprocess.run(command, capture_output=True, text=True)
                parse_result(result, "nvol_partitions", f"{file}_{str(partition)}_stats")
            else:
                print("WRONG TYPE")

            # command = ["gpmetis", f"../graphs/{file}", str(partition)] if type != "rg-mk" else ["gpmetis", f"../graphs/{file}", str(partition), "-objtype=rg-mk"]
            # result = subprocess.run(command, capture_output=True, text=True)
            # parse_result(result, "cut_partitions", f"{file}_{str(partition)}_stats") if type != "rg-mk" else parse_result(result, "rg-mk_partitions", f"{file}_{str(partition)}_stats")

    if type == "rg-mk":
        move_files("rg-mk_partitions")
        # move_files("enhanced_boundary_partitions")
    elif type == "cut":
        move_files("cut_partitions")
    elif type == "nvol":
        move_files("nvol_partitions")
        
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

    for line in output.stdout.splitlines():
        if "Edgecut:" in line and "communication volume" in line:
            ed_ind = line.find("Edgecut: ") + len("edgecut:")
            cv_ind = line.find("communication volume: ") + len("communication volume: ")
            ed = line[ed_ind:line.find(",")].strip()
            cv = line[cv_ind:line.find(".")].strip()

        elif "constraint #0: " in line:
            balance = line[line.find("constraint #0: ") + len("constraint #0:"):]
    
        elif "I/O: " in line: 
            io_time = line[line.find("I/O: ") + len("I/O: "):].strip()

        elif  "Partitioning: " in line: 
            pt_time = line[line.find("Partitioning: ") + len("Partitioning: "): line.find("(")].strip()

        elif "Reporting: " in line: 
            rep_time = line[line.find("Reporting: ") + len("Reporting: "):].strip()
        
    write_metrics_to_file(f"../{destination}/stats/{file}.txt", ed, cv, balance, io_time, pt_time, rep_time)

def write_metrics_to_file(path, ed, cv, balance, io_time, pt_time, rep_time):
    with open(path, "w") as f:
        f.write("=== Partitioning Results ===\n")
        if ed is not None:
            f.write(f"Edgecut:            {ed}\n")
        if cv is not None:
            f.write(f"Communication Vol.: {cv}\n")
        if balance is not None:
            f.write(f"Balance:            {balance}\n")
        if io_time is not None:
            f.write(f"I/O Time:           {io_time}\n")
        if pt_time is not None:
            f.write(f"Partition Time:     {pt_time}\n")
        if rep_time is not None:
            f.write(f"Reporting Time:     {rep_time}\n")

run_metis("rg-mk", ["roadsCA_graph"])
run_metis("rg-mk", files_cube)
run_metis("rg-mk", files_grid)
run_metis("rg-mk", ["skitter_graph"])
run_metis("rg-mk", ["deezer_graph"])

run_metis("cut", ["roadsCA_graph"])
run_metis("cut", files_cube)
run_metis("cut", files_grid)
run_metis("cut", ["skitter_graph"])
run_metis("cut", ["deezer_graph"])