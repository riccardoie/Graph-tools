import matplotlib.pyplot as plt
import numpy as np

# X-axis labels (megatest numbers)
megatests = np.array([4, 5, 10, 20, 25])

# Data (two values per test — e.g., time or measurement)
default = np.array([2795, 3520, 6340, 9473, 11085])
enhanced = np.array([2797, 3540, 6318, 9523, 11091])

# Create a plot
plt.figure(figsize=(9, 5))

# Plot both lines
plt.plot(megatests, default, marker='o', linestyle='-', color='b', label='Default')
plt.plot(megatests, enhanced, marker='s', linestyle='--', color='r', label='Enhanced Boundary')

# Add titles and labels
plt.title("Performance Comparison: Default vs. Enhanced Boundary")
plt.xlabel("Megatest")
plt.ylabel("Value")

# Add grid and legend
plt.grid(True)
plt.legend()

# Display the graph
plt.show()