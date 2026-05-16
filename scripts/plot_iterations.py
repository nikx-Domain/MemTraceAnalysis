import os
import sys
import json
import glob

try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib or numpy not installed. Visualizations will not be generated.")
    print("Install with: pip install matplotlib numpy")

def plot_error_bars(stats, metric, out_path, title=""):
    if metric not in stats.get('cpp_4kb', {}) or metric not in stats.get('cpp_2mb', {}):
        return
        
    labels = ['4KB Pages', '2MB HugePages']
    means = [stats['cpp_4kb'][metric]['mean'], stats['cpp_2mb'][metric]['mean']]
    stdevs = [stats['cpp_4kb'][metric]['stdev'], stats['cpp_2mb'][metric]['stdev']]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, means, yerr=stdevs, align='center', alpha=0.7, ecolor='black', capsize=10)
    ax.set_ylabel(metric)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_title(title if title else f'C++ {metric} Comparison (Mean ± StdDev)')
    ax.yaxis.grid(True)
    
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_trend(results_dir, config, metric, out_path):
    pattern = os.path.join(results_dir, f"{config}_iter*.csv")
    files = glob.glob(pattern)
    
    data_points = []
    for f in files:
        basename = os.path.basename(f)
        try:
            iter_num = int(basename.split('_iter')[1].split('.csv')[0])
        except ValueError:
            continue
            
        with open(f, 'r') as csvfile:
            for line in csvfile:
                if metric in line:
                    parts = line.split(',')
                    try:
                        val = float(parts[0])
                        data_points.append((iter_num, val))
                    except ValueError:
                        pass
                        
    if not data_points: return
    data_points.sort()
    iters = [d[0] for d in data_points]
    vals = [d[1] for d in data_points]
    
    plt.figure(figsize=(10, 5))
    plt.plot(iters, vals, marker='o', linestyle='-', color='b')
    plt.title(f'Trend over Iterations: {config.upper()} - {metric}')
    plt.xlabel('Iteration')
    plt.ylabel(metric)
    plt.grid(True)
    plt.xticks(iters)
    
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def extract_metric_list(results_dir, config, metric):
    pattern = os.path.join(results_dir, f"{config}_iter*.csv")
    files = glob.glob(pattern)
    vals = []
    for f in files:
        with open(f, 'r') as csvfile:
            for line in csvfile:
                if metric in line:
                    parts = line.split(',')
                    try:
                        vals.append(float(parts[0]))
                    except ValueError:
                        pass
    return vals

def plot_box(results_dir, metric, title, out_path):
    cpp_4kb = extract_metric_list(results_dir, 'cpp_4kb', metric)
    cpp_2mb = extract_metric_list(results_dir, 'cpp_2mb', metric)
    
    if not cpp_4kb or not cpp_2mb: return
    
    plt.figure(figsize=(8, 6))
    plt.boxplot([cpp_4kb, cpp_2mb], labels=['4KB Pages', '2MB HugePages'])
    plt.title(title)
    plt.ylabel(metric)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    
def extract_p99_latency(results_dir, config):
    pattern = os.path.join(results_dir, f"{config}_latency_iter*.txt")
    files = glob.glob(pattern)
    
    data_points = []
    for f in files:
        basename = os.path.basename(f)
        try:
            iter_num = int(basename.split('_iter')[1].split('.txt')[0])
        except ValueError:
            continue
            
        with open(f, 'r') as txtfile:
            p99_val = None
            for line in txtfile:
                if '%' in line and '<=' in line and 'milliseconds' in line:
                    try:
                        pct_str = line.split('%')[0].strip()
                        pct = float(pct_str)
                        if pct >= 99.0 and p99_val is None:
                            val_str = line.split('<=')[1].split('milliseconds')[0].strip()
                            p99_val = float(val_str)
                    except ValueError:
                        pass
            if p99_val is not None:
                data_points.append((iter_num, p99_val))
                        
    data_points.sort()
    return data_points

def plot_p99_comparison(results_dir, out_path):
    redis_4kb = extract_p99_latency(results_dir, 'redis_4kb')
    redis_2mb = extract_p99_latency(results_dir, 'redis_2mb')
    
    if not redis_4kb or not redis_2mb: return
    
    plt.figure(figsize=(10, 5))
    
    iters_4kb = [d[0] for d in redis_4kb]
    vals_4kb = [d[1] for d in redis_4kb]
    
    iters_2mb = [d[0] for d in redis_2mb]
    vals_2mb = [d[1] for d in redis_2mb]
    
    plt.plot(iters_4kb, vals_4kb, marker='o', linestyle='-', color='b', label='Redis 4KB')
    plt.plot(iters_2mb, vals_2mb, marker='s', linestyle='-', color='r', label='Redis 2MB (THP)')
    
    if vals_2mb:
        mean_2mb = np.mean(vals_2mb)
        for i, val in enumerate(vals_2mb):
            if val > 3 * mean_2mb:
                plt.plot(iters_2mb[i], val, 'rX', markersize=12) 
                
    plt.title('Redis P99 Latency Comparison (Spikes = Compaction Events)')
    plt.xlabel('Iteration')
    plt.ylabel('P99 Latency (ms)')
    plt.legend()
    plt.grid(True)
    plt.xticks(iters_4kb)
    
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_all_dtlb_misses(stats, out_path):
    configs = ['cpp_4kb', 'cpp_2mb', 'redis_4kb', 'redis_2mb', 'nginx_4kb', 'nginx_2mb']
    labels = ['C++ 4KB', 'C++ 2MB', 'Redis 4KB', 'Redis 2MB', 'Nginx 4KB', 'Nginx 2MB']
    colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown']
    means = []
    stdevs = []
    
    for c in configs:
        if c in stats and 'dTLB-load-misses' in stats[c]:
            means.append(stats[c]['dTLB-load-misses']['mean'])
            stdevs.append(stats[c]['dTLB-load-misses']['stdev'])
        else:
            means.append(0)
            stdevs.append(0)
            
    fig, ax = plt.subplots(figsize=(12, 6))
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, means, yerr=stdevs, align='center', alpha=0.7, ecolor='black', capsize=10, color=colors)
    ax.set_ylabel('dTLB Load Misses')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=15)
    ax.set_title('dTLB Miss Configuration Graph (All Workloads)')
    ax.yaxis.grid(True)
    
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_all_ipc(stats, out_path):
    configs = ['cpp_4kb', 'cpp_2mb', 'redis_4kb', 'redis_2mb', 'nginx_4kb', 'nginx_2mb']
    labels = ['C++ 4KB', 'C++ 2MB', 'Redis 4KB', 'Redis 2MB', 'Nginx 4KB', 'Nginx 2MB']
    colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown']
    ipcs = []
    
    for c in configs:
        if c in stats and 'instructions' in stats[c] and 'cycles' in stats[c]:
            instr = stats[c]['instructions']['mean']
            cycles = stats[c]['cycles']['mean']
            ipc = instr / cycles if cycles > 0 else 0
            ipcs.append(ipc)
        else:
            ipcs.append(0)
            
    fig, ax = plt.subplots(figsize=(12, 6))
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, ipcs, align='center', alpha=0.7, color=colors)
    ax.set_ylabel('Instructions Per Cycle (IPC)')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=15)
    ax.set_title('IPC Hardware Level Metrics (All Workloads)')
    ax.yaxis.grid(True)
    
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def extract_redis_throughput(results_dir, config):
    pattern = os.path.join(results_dir, f"{config}_latency_iter*.txt")
    files = glob.glob(pattern)
    throughputs = []
    
    for f in files:
        with open(f, 'r') as txtfile:
            for line in txtfile:
                if 'throughput summary:' in line:
                    try:
                        val = float(line.split(':')[1].replace('requests per second', '').strip())
                        throughputs.append(val)
                    except (IndexError, ValueError):
                        pass
    if throughputs:
        return np.mean(throughputs), np.std(throughputs)
    return 0, 0

def plot_redis_throughput(results_dir, out_path):
    mean_4kb, std_4kb = extract_redis_throughput(results_dir, 'redis_4kb')
    mean_2mb, std_2mb = extract_redis_throughput(results_dir, 'redis_2mb')
    
    if mean_4kb == 0 and mean_2mb == 0: return
    
    labels = ['Redis 4KB', 'Redis 2MB (THP)']
    means = [mean_4kb, mean_2mb]
    stdevs = [std_4kb, std_2mb]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, means, yerr=stdevs, align='center', alpha=0.7, ecolor='black', capsize=10, color=['orange', 'red'])
    ax.set_ylabel('Requests Per Second')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_title('Redis Throughput Comparison')
    ax.yaxis.grid(True)
    
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def extract_nginx_throughput(results_dir, config):
    pattern = os.path.join(results_dir, f"{config}_latency_iter*.txt")
    files = glob.glob(pattern)
    throughputs = []
    
    for f in files:
        with open(f, 'r') as txtfile:
            for line in txtfile:
                if 'Requests/sec:' in line:
                    try:
                        val = float(line.split(':')[1].strip())
                        throughputs.append(val)
                    except (IndexError, ValueError):
                        pass
    if throughputs:
        return np.mean(throughputs), np.std(throughputs)
    return 0, 0

def plot_nginx_throughput(results_dir, out_path):
    mean_4kb, std_4kb = extract_nginx_throughput(results_dir, 'nginx_4kb')
    mean_2mb, std_2mb = extract_nginx_throughput(results_dir, 'nginx_2mb')
    
    if mean_4kb == 0 and mean_2mb == 0: return
    
    labels = ['Nginx 4KB', 'Nginx 2MB (THP)']
    means = [mean_4kb, mean_2mb]
    stdevs = [std_4kb, std_2mb]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, means, yerr=stdevs, align='center', alpha=0.7, ecolor='black', capsize=10, color=['purple', 'brown'])
    ax.set_ylabel('Requests Per Second')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_title('Nginx Throughput Comparison (wrk benchmark)')
    ax.yaxis.grid(True)
    
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def main():
    if not HAS_MATPLOTLIB:
        return
        
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "results/iterations"

    stats_file = os.path.join(results_dir, "aggregated_stats.json")
    if not os.path.exists(stats_file):
        print(f"Stats file {stats_file} not found. Run aggregate_iterations.py first.")
        return
        
    with open(stats_file, 'r') as f:
        stats = json.load(f)
        
    os.makedirs(results_dir, exist_ok=True)
    
    # 1. Baseline Comparison Graphs (all 6 configs)
    plot_error_bars(stats, 'page-faults', os.path.join(results_dir, 'cpp_page_faults_bar.png'), title='Total Page Faults (C++ Synthetic)')
    plot_all_dtlb_misses(stats, os.path.join(results_dir, 'dtlb_misses.png'))
    plot_all_ipc(stats, os.path.join(results_dir, 'ipc_comparison.png'))
    plot_redis_throughput(results_dir, os.path.join(results_dir, 'redis_throughput_bar.png'))
    plot_nginx_throughput(results_dir, os.path.join(results_dir, 'nginx_throughput_bar.png'))
    
    # 2. C++ Iteration Variance Graphs
    plot_box(results_dir, 'page-faults', 'C++ Page Faults Distribution', os.path.join(results_dir, 'cpp_page_faults_distribution.png'))
    plot_box(results_dir, 'dTLB-load-misses', 'C++ dTLB Misses Distribution', os.path.join(results_dir, 'cpp_dtlb_misses_distribution.png'))
    
    # 3. Redis Tail Latency & Fragmentation
    plot_p99_comparison(results_dir, os.path.join(results_dir, 'redis_p99_latency_comparison.png'))
    plot_trend(results_dir, 'redis_2mb', 'dTLB-load-misses', os.path.join(results_dir, 'redis_dtlb_trend.png'))
    
    # 4. Nginx Fragmentation Trends
    plot_trend(results_dir, 'nginx_4kb', 'dTLB-load-misses', os.path.join(results_dir, 'nginx_4kb_dtlb_trend.png'))
    plot_trend(results_dir, 'nginx_2mb', 'dTLB-load-misses', os.path.join(results_dir, 'nginx_2mb_dtlb_trend.png'))
    
    print("Plots generated in", results_dir)

if __name__ == "__main__":
    main()
