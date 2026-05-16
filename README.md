# Linux Memory Performance Analysis: The "Performance Cliff"

This project empirically evaluates the performance impact of memory page granularity—specifically comparing standard **4KB Pages** against **2MB Transparent HugePages (THP)** across different application access patterns.

## Project Overview

Modern applications often allocate gigabytes of memory. However, the CPU manages this memory in tiny 4KB blocks called "pages". When applications access memory across wide, disjointed regions, the CPU's Translation Lookaside Buffer (TLB) thrashes, causing severe performance degradation known as the "Performance Cliff". 

This project explores this cliff by measuring Hardware Performance Counters (like TLB misses and Page Faults) across three specific access patterns:
1. **Predictable Linear Access (C++ Workload):** Directly stresses the system's memory allocation mapping via `mmap`.
2. **Predictable Sequential Access (Nginx):** Tests linear file caching via the `sendfile()` syscall.
3. **Randomized Chaotic Access (Redis):** Uses Hash Maps to intentionally fracture CPU cache predictions.

## Repository Structure

```text
├── src/                # Core C++ workload generator source code
├── scripts/            # Bash and Python telemetry and execution scripts
├── results/            # Generated performance plots and raw CSV data
├── viva_prep/          # Viva and presentation guide
├── IEEE_Report.md      # Full academic project report detailing findings
├── run_all.sh          # Master execution script
└── Makefile            # Build configuration
```

## Prerequisites

To run the telemetry collection, you must be on a **Linux System** with the following tools installed:
- `g++` and `make` (for compiling the workload)
- `perf` (Linux Performance Events tool for reading hardware counters)
- `vmstat`
- `python3` with `matplotlib` (for generating graphs)

*(Note: Hardware telemetry collection via `perf` will not work on macOS or environments where hypervisors block Performance Monitor Counters)*

## How to Run the Project

### 1. Build the Workload
Compile the C++ memory workload generator:
```bash
make
```

### 2. Run the Full Suite
The master script will automatically configure kernel parameters, execute the workloads (C++ and Redis), and dump the CSV outputs into the `results/` directory:
```bash
./run_all.sh
```

*(Alternatively, you can run workloads individually and collect data for a specific duration using `scripts/measure_all.sh <duration_secs> <name>`)*

### 3. Generate Visualizations
Once the `_perf.csv` files have been generated in the `results/` folder, run the Python plotting scripts to visualize the "Performance Cliff":
```bash
python3 scripts/plot_results.py
python3 scripts/generate_final_graphs.py
```
Your generated PNG graphs will be saved to the `results/` directory!

## Results Highlights
Our findings (detailed in `IEEE_Report.md`) prove that adopting 2MB HugePages drastically reduces Page Faults by **over 99%** for linear workloads, and acts as a "hardware parachute" to rescue randomly-accessed databases like Redis from severe translation bottlenecks.
