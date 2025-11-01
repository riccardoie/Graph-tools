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
        n = int(file[:file.find("_")])

        for partition in partitions:

            if(not n*n*n >= partition * partition):
                break
            command = ["gpmetis", f"../graphs/{file}", str(partition)] if type != "rg-mk" else ["gpmetis", f"../graphs/{file}", str(partition), "-objtype=rg-mk"]
            result = subprocess.run(command, capture_output=True, text=True)
            parse_result(result, "cut_partitions", f"{file}_{str(partition)}_stats") if type != "rg-mk" else parse_result(result, "rg-mk_partitions", f"{file}_{str(partition)}_stats")

    move_files("cut_partitions") if type != "rg-mk" else move_files("rg-mk_partitions")


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

# run_metis("rg-mk", files_grid)
