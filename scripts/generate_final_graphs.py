import os
import matplotlib.pyplot as plt
import numpy as np

# Output Directory
results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(results_dir, exist_ok=True)

# --- DATA FROM VM OUTPUT ---
labels_cpp = ['C++ Sequential (4KB)', 'C++ Sequential (2MB)']
page_faults_cpp = [131456, 384]
elapsed_time_cpp = [0.2148, 0.00238]

labels_redis = ['Redis (THP Disabled)', 'Redis (THP Enabled)']
redis_set = [264550.28, 280504.91]
redis_get = [279095.72, 280583.62]

# 1. Bar Graph: Page Faults (C++ Workload)
plt.figure(figsize=(8, 6))
plt.bar(labels_cpp, page_faults_cpp, color=['lightcoral', 'lightgreen'])
plt.title('Page Faults: Standard 4KB vs 2MB HugePages')
plt.ylabel('Number of Page Faults (Lower is Better)')
plt.yscale('log') # Log scale since difference is massive
for i, v in enumerate(page_faults_cpp):
    plt.text(i, v, str(v), ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'cpp_page_faults_bar.png'))
plt.close()

# 2. Bar Graph: Redis Throughput
x = np.arange(len(labels_redis))
width = 0.35
fig, ax = plt.subplots(figsize=(8, 6))
rects1 = ax.bar(x - width/2, redis_set, width, label='SET (req/s)', color='#ff9999')
rects2 = ax.bar(x + width/2, redis_get, width, label='GET (req/s)', color='#66b3ff')
ax.set_ylabel('Requests per Second (Higher is Better)')
ax.set_title('Redis Throughput Comparison')
ax.set_xticks(x)
ax.set_xticklabels(labels_redis)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'redis_throughput_bar.png'))
plt.close()

# 3. Line Graph: Execution Time Drop
plt.figure(figsize=(8, 6))
plt.plot(labels_cpp, elapsed_time_cpp, marker='o', linestyle='-', color='purple', markersize=10, linewidth=2)
plt.title('Execution Time Drop (C++ Workload)')
plt.ylabel('Time in Seconds (Lower is Better)')
plt.grid(True, linestyle='--', alpha=0.6)
for i, v in enumerate(elapsed_time_cpp):
    plt.text(i, v + 0.01, f'{v:.4f}s', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'cpp_execution_time_line.png'))
plt.close()

# 4. Bar Graph: Nginx Throughput
labels_nginx = ['Nginx (4KB Pages)', 'Nginx (2MB THP)']
nginx_throughput = [5.67, 6.41]

plt.figure(figsize=(8, 6))
plt.bar(labels_nginx, nginx_throughput, color=['#c2c2f0', '#ffb3e6'], width=0.5)
plt.title('Nginx Network Throughput Comparison')
plt.ylabel('Throughput in GB/s (Higher is Better)')
plt.ylim(0, 8) # Set y-limit slightly above max value for better visuals
for i, v in enumerate(nginx_throughput):
    plt.text(i, v + 0.1, f'{v} GB/s', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(results_dir, 'nginx_throughput_bar.png'))
plt.close()

print("Graphs successfully generated in results/ directory!")
