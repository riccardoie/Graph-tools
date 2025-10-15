import subprocess
import os
import shutil


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




run_metis("def", files_cube)