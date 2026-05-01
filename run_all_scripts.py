import run_metis
import calc_partitions
import form_statics

files_grid = ["4_graph", "10_graph", "15_graph", "20_graph", "100_graph", "1000_graph"]
files_cube = ["3_cube_graph", "5_cube_graph", "10_cube_graph", "100_cube_graph"]

# files_heart = ["heart01_graph", "heart02_graph", "heart03_graph", "heart04_graph", "heart05_graph", "heart06_graph", "heart07_graph"]

# files_heart = ["heart06_graph", "heart07_graph", "pa2010_graph", "coPapersDBLP_graph"]
glisne_matrixes = ["fe_tooth_graph", "pa2010_graph", "roadNet-CA_graph","channel-500x100x100-b050_graph",
                    "hugetric-00000_graph", "hugetric-00020_graph", "hugetrace-00020_graph", "italy_osm_graph", 
                    "europe_osm_graph", "citationCiteseer_graph"]

# glisne_matrixes = ["coPapersDBLP_graph", "kmer_U1a_graph", "kmer_V2a_graph"]
# glisne_matrixes = []

# glisne_matrixes = ["coPapersDBLP_graph"]
folder = "nvol_08"
type = "nvol"

# run_metis.run_metis(type, files_grid, folder)
# for file in files_grid:
#     calc_partitions.form_volstats(file, folder)
#     print("Finished " + file)

# run_metis.run_metis(type, files_cube, folder)
# for file in files_cube:
#     calc_partitions.form_volstats(file, folder)
#     print("Finished " + file)

# run_metis.run_metis(type, files_heart, folder)
# for file in files_heart:
#     calc_partitions.form_volstats(file, folder)
#     print("Finished " + file)

run_metis.run_metis(type, glisne_matrixes, folder)
for file in glisne_matrixes:
    calc_partitions.form_volstats(file, folder)
    print("Finished " + file)


form_statics.form_stats(folder)