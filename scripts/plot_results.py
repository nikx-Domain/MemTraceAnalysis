#!/usr/bin/env python3
import os
import glob
import matplotlib.pyplot as plt

def read_perf_csv(filename):
    data = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'): continue
            parts = line.strip().split(',')
            if len(parts) >= 3:
                val = parts[0]
                event = parts[2]
                if val.isdigit() or val.replace('.','',1).isdigit():
                    data[event] = float(val)
    return data

def main():
    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    perf_files = glob.glob(os.path.join(results_dir, '*_perf.csv'))
    
    if not perf_files:
        print("No perf csv files found.")
        return
        
    labels = []
    dtlb_misses = []
    page_faults = []
    ipc_values = []
    
    for pf in perf_files:
        basename = os.path.basename(pf).replace('_perf.csv', '')
        labels.append(basename)
        
        data = read_perf_csv(pf)
        loads = data.get('dTLB-load-misses', 0)
        stores = data.get('dTLB-store-misses', 0)
        dtlb_misses.append(loads + stores)
        
        page_faults.append(data.get('page-faults', 0))

        # IPC Calculation (Instructions Per Cycle)
        cycles = data.get('cycles', 0)
        instr = data.get('instructions', 0)
        ipc = (instr / cycles) if cycles > 0 else 0
        ipc_values.append(ipc)
        
    # Plot 1: Page Faults (Fallback for VM where dTLB is unsupported)
    plt.figure(figsize=(10,6))
    plt.bar(labels, page_faults, color='lightcoral')
    plt.title('Page Faults across Configurations')
    plt.ylabel('Total Page Faults')
    plt.xticks(rotation=45)
    plt.tight_layout()
    miss_path = os.path.join(results_dir, 'page_faults.png')
    plt.savefig(miss_path)
    
    # Plot 2: IPC (Instructions Per Cycle)
    plt.figure(figsize=(10,6))
    plt.bar(labels, ipc_values, color='lightgreen')
    plt.title('IPC (Instructions Per Cycle)')
    plt.ylabel('IPC (Higher is Better)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    ipc_path = os.path.join(results_dir, 'ipc_comparison.png')
    plt.savefig(ipc_path)

    # Plot 3: dTLB Misses
    plt.figure(figsize=(10,6))
    plt.bar(labels, dtlb_misses, color='orange')
    plt.title('dTLB Misses across Configurations')
    plt.ylabel('Total dTLB Misses (Lower is Better)')
    plt.yscale('log') # Use log scale for large differences
    plt.xticks(rotation=45)
    plt.tight_layout()
    dtlb_path = os.path.join(results_dir, 'dtlb_misses.png')
    plt.savefig(dtlb_path)

    print(f"Metrics parsed successfully!")
    print(f"-> Saved: {miss_path}")
    print(f"-> Saved: {ipc_path}")
    print(f"-> Saved: {dtlb_path}")

if __name__ == '__main__':
    main()
