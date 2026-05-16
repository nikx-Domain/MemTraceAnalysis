import os
import glob
import sys
import json

def get_iterations_data(config, results_dir):
    pattern = os.path.join(results_dir, f"{config}_iter*.csv")
    files = glob.glob(pattern)
    data = {}
    
    for f in files:
        basename = os.path.basename(f)
        try:
            iter_num = int(basename.split('_iter')[1].split('.csv')[0])
        except ValueError:
            continue
            
        with open(f, 'r') as csvfile:
            metrics = {}
            for line in csvfile:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = line.split(',')
                if len(parts) >= 3:
                    try:
                        if '<not counted>' in parts[0]: continue
                        val = float(parts[0])
                        event = parts[2]
                        metrics[event] = val
                    except ValueError:
                        continue
            data[iter_num] = metrics
    return data

def main():
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "results/iterations"

    configs = ["cpp_4kb", "cpp_2mb", "redis_4kb", "redis_2mb", "nginx_4kb", "nginx_2mb"]
    
    print("FRAGMENTATION TREND ANALYSIS\n")
    for config in configs:
        data = get_iterations_data(config, results_dir)
        if not data: continue
        
        iterations = sorted(data.keys())
        if len(iterations) < 2: continue
        
        first_iter = iterations[0]
        last_iter = iterations[-1]
        
        print(f"Fragmentation Analysis ({config.upper()}):")
        
        events_to_check = ['dTLB-load-misses', 'page-faults', 'major-faults']
        available_events = set()
        for v in data.values():
            available_events.update(v.keys())
            
        for event in events_to_check:
            if event not in available_events: continue
            
            first_val = data[first_iter].get(event, 0)
            last_val = data[last_iter].get(event, 0)
            
            if first_val == 0: continue
            
            pct_change = ((last_val - first_val) / first_val) * 100
            
            critical_marker = " <- CRITICAL" if pct_change > 5 else ""
            print(f"  - {event}: Iteration {first_iter} = {first_val:,.0f}, Iteration {last_iter} = {last_val:,.0f}, {pct_change:+.2f}% degradation{critical_marker}")

if __name__ == "__main__":
    main()
