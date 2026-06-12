import run_metis
import calc_partitions
import form_statics

files_grid = ["4_graph", "10_graph", "15_graph", "20_graph", "100_graph", "1000_graph"]
files_cube = ["3_cube_graph", "5_cube_graph", "10_cube_graph", "100_cube_graph"]

files_heart = ["heart01_graph", "heart02_graph", "heart03_graph", "heart04_graph", "heart05_graph", "heart06_graph", "heart07_graph"]

files_heart = ["heart02_graph", "heart03_graph", "heart04_graph", "heart05_graph", "heart06_graph", "heart07_graph"]

glisne_matrixes = ["pa2010_graph", "hugetric-00020_graph", "hugetrace-00020_graph", "packing-500x100x100-b050_graph", "delaunay_n24_graph", "delaunay_n23_graph"]

# glisne_matrixes = ["hugetric-00000_graph", "hugetric-00020_graph", "hugetrace-00020_graph", "italy_osm_graph", 
                    # "delaunay_n23_graph", "packing-500x100x100-b050_graph", "rgg_n_2_23_s0_graph"]



# glisne_matrixes = ["hugetric-00020_graph", "delaunay_n23_graph", "delaunay_n24_graph", "packing-500x100x100-b050_graph","hugetrace-00020_graph"]
# glisne_matrixes = ["delaunay_n24_graph", "rgg_n_2_23_s0_graph"] 
glisne_matrixes = [ "europe_osm_graph"]

folder = "nvol_08_4"
type = "nvol_4"

# folder = "vol_partitions"
# type = "vol"
# run_metis.run_metis(type, files_grid, folder)
# for file in files_grid:
#     calc_partitions.outgoing_volstats(file, folder)
#     print("Finished " + file)

# run_metis.run_metis(type, files_cube, folder)
# for file in files_cube:
#     calc_partitions.outgoing_volstats(file, folder)
#     print("Finished " + file)

# run_metis.run_metis(type, files_heart, folder)
# for file in files_heart:
# # #     calc_partitions.outgoing_volstats(file, folder)
#     calc_partitions.incoming_volstats(file, folder)
#     print("Finished " + file)

run_metis.run_metis(type, glisne_matrixes, folder)
for file in glisne_matrixes:
    # calc_partitions.incoming_volstats(file, folder)
    calc_partitions.outgoing_volstats(file, folder)
#     print("Finished " + file)


form_statics.form_stats(folder)