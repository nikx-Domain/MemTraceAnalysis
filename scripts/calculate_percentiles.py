import os
import glob
import statistics
import sys

def main():
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "results/iterations"

    configs = ["redis_4kb", "redis_2mb"]
    
    for config in configs:
        pattern = os.path.join(results_dir, f"{config}_latency_iter*.txt")
        files = glob.glob(pattern)
        
        if not files:
            continue
            
        p99_values = {}
        for f in files:
            basename = os.path.basename(f)
            iter_num_str = basename.split('_iter')[1].split('.txt')[0]
            try:
                iter_num = int(iter_num_str)
            except ValueError:
                continue
                
            with open(f, 'r') as txtfile:
                for line in txtfile:
                    if '99.00%' in line or '99.000%' in line:
                        try:
                            val_str = line.split(':')[1].replace('ms', '').strip()
                            p99_values[iter_num] = float(val_str)
                        except (IndexError, ValueError):
                            pass
                            
        if not p99_values: continue
        
        values_list = list(p99_values.values())
        mean_p99 = statistics.mean(values_list)
        stdev_p99 = statistics.stdev(values_list) if len(values_list) > 1 else 0
        
        print(f"\n[LATENCY ANALYSIS: {config.upper()}]")
        print(f"Mean P99: {mean_p99:.2f} ms, StdDev: {stdev_p99:.2f} ms")
        
        anomalies = False
        print("ANOMALIES DETECTED:")
        for iter_num in sorted(p99_values.keys()):
            val = p99_values[iter_num]
            if val > 3 * mean_p99:
                anomalies = True
                ratio = val / mean_p99
                print(f"  Iteration {iter_num}: {val:.2f} ms ({ratio:.2f}x mean) <- Compaction event?")
                
        if not anomalies:
            print("  None detected.")

if __name__ == "__main__":
    main()
