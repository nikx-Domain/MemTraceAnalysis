#!/bin/bash
# Usage: ./run_suite.sh <SIZE_MB> <NUM_ITERATIONS> <CONFIG_NAME>

SIZE=$1
NUM_ITERATIONS=${2:-5}
TAG=$3

if [ -z "$TAG" ]; then
    echo "Usage: ./run_suite.sh <SIZE_MB> <NUM_ITERATIONS> <CONFIG_NAME>"
    exit 1
fi

mkdir -p results/iterations/${TAG}/

for i in $(seq 1 $NUM_ITERATIONS); do
    echo "[Iteration $i/$NUM_ITERATIONS] Running..."
    # 1. Clear OS Caches
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    
    # 2. Run with perf
    perf stat -x, -o results/iterations/${TAG}/iteration_${i}.csv -e dTLB-load-misses,page-faults,instructions,cycles,minor-faults,major-faults \
        ./bin/workload $SIZE 0 2> /dev/null
        
    sleep 2
    echo "Completed iteration $i"
done
