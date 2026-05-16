import os
import glob
import sys
import json
import statistics
import math

def calculate_percentile(data, percentile):
    size = len(data)
    if size == 0: return 0
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]

def main():
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "results/iterations"

    configs = ["cpp_4kb", "cpp_2mb", "redis_4kb", "redis_2mb", "nginx_4kb", "nginx_2mb"]
    
    aggregated_data = {}
    
    for config in configs:
        pattern = os.path.join(results_dir, f"{config}_iter*.csv")
        files = glob.glob(pattern)
        
        if not files:
            continue
            
        metrics = {}
        for f in files:
            with open(f, 'r') as csvfile:
                for line in csvfile:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            if '<not counted>' in parts[0]: continue
                            val = float(parts[0])
                            event = parts[2]
                            if event not in metrics:
                                metrics[event] = []
                            metrics[event].append(val)
                        except ValueError:
                            continue
                            
        if not metrics: continue
        
        config_stats = {}
        print(f"[{config.upper()}]")
        for event, values in metrics.items():
            if not values: continue
            mean = statistics.mean(values)
            stdev = statistics.stdev(values) if len(values) > 1 else 0
            config_stats[event] = {
                "mean": mean,
                "stdev": stdev,
                "min": min(values),
                "max": max(values),
                "p50": calculate_percentile(values, 50),
                "p95": calculate_percentile(values, 95),
                "p99": calculate_percentile(values, 99)
            }
            print(f"  {event}: {mean:,.2f} ± {stdev:,.2f}")
            print(f"    P99 (Tail): {config_stats[event]['p99']:,.2f}")
        
        aggregated_data[config] = config_stats
        
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "aggregated_stats.json")
    with open(output_path, 'w') as f:
        json.dump(aggregated_data, f, indent=2)
        
    print(f"\nSaved aggregated stats to {output_path}")

if __name__ == "__main__":
    main()
