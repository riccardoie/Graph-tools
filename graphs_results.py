import matplotlib.pyplot as plt
import numpy as np

# X-axis labels (megatest numbers)
megatests = [4, 5, 10, 20, 25]

# Data (two values per test — e.g., time or measurement)
default = np.array([2795, 3520, 6340, 9473, 11085])
enhanced = np.array([2797, 3540, 6318, 9523, 11091])

# X locations for bars
x = np.arange(len(megatests))
width = 0.35  # width of each bar

plt.bar(x - width/2, default, width, label='default metis', color='skyblue')
plt.bar(x + width/2, enhanced, width, label='metis with greater boundery list', color='orange')

plt.xlabel('Nr of partitions')
plt.ylabel('Total edge cut')
plt.title('Difference in edge cut on 1.000.000 node grid graph')
plt.xticks(x, megatests)
plt.legend()

# Optional: add value labels
for i in range(len(megatests)):
    plt.text(x[i] - width/2, default[i] + 1, str(default[i]), ha='center')
    plt.text(x[i] + width/2, enhanced[i] + 1, str(enhanced[i]), ha='center')

# Show plot
plt.show()