import matplotlib.pyplot as plt
import numpy as np
import os

# Data
metrics = ['Positive Assertion', 'Negative Assertion', 'Current Temporality', 'Attribute Completeness']
error_rates = [0.2618, 0.2728, 0.1535, 0.2823]
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']

# Create output dir if not exists
output_dir = 'assets'
# Since we are in the main project directory
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. Bar Chart for Average Error Rates
plt.figure(figsize=(10, 6))
bars = plt.bar(metrics, error_rates, color=colors)
plt.title('Average Error Rates by Category', fontsize=16, pad=20)
plt.ylabel('Error Rate', fontsize=12)
plt.ylim(0, 0.5)

# Add value labels
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f'{yval:.1%}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'error_rates_bar_chart.png'), dpi=300)
plt.close()

# 2. File-wise Comparison
files = ['Chart 1', 'Chart 2', 'Chart 3', 'Chart 4']
pos_assert = [0.2053, 0.1335, 0.3434, 0.3648]
neg_assert = [0.2278, 0.2857, 0.4815, 0.0962]
curr_temp = [0.1897, 0.0491, 0.1278, 0.2475]
attr_comp = [0.2619, 0.1996, 0.4021, 0.2656]

x = np.arange(len(files))
width = 0.2

fig, ax = plt.subplots(figsize=(12, 7))
rects1 = ax.bar(x - 1.5*width, pos_assert, width, label='Positive Assertion', color=colors[0])
rects2 = ax.bar(x - 0.5*width, neg_assert, width, label='Negative Assertion', color=colors[1])
rects3 = ax.bar(x + 0.5*width, curr_temp, width, label='Current Temporality', color=colors[2])
rects4 = ax.bar(x + 1.5*width, attr_comp, width, label='Attribute Completeness', color=colors[3])

ax.set_ylabel('Error Rate', fontsize=12)
ax.set_title('Error Rates Across Sample Charts', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(files)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'file_comparison_chart.png'), dpi=300, bbox_inches='tight')
plt.close()

print("Graphs generated successfully in 'assets' directory.")
