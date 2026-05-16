#!/bin/bash
# Description: Wrapper to collect vmstat and perf metrics over a period.
# Usage: ./measure_all.sh <duration_seconds> <workload_name> <num_iterations>

DURATION=$1
NAME=$2
NUM_ITERATIONS=${3:-5}

if [ -z "$NAME" ] || [ -z "$DURATION" ]; then
    echo "Usage: $0 <duration_in_secs> <workload_name> [num_iterations]"
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESULTS_DIR="$DIR/../results/iterations/${NAME}"
mkdir -p "$RESULTS_DIR"

echo "=== Telemetry Collection: $NAME for ${DURATION}s (Iterations: $NUM_ITERATIONS) ==="

for i in $(seq 1 $NUM_ITERATIONS); do
    echo "  Iteration $i/$NUM_ITERATIONS"
    
    # Clear OS Caches
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

    # vmstat every 1 second
    vmstat 1 $DURATION > "$RESULTS_DIR/${NAME}_vmstat_iter${i}.txt" &
    VM_PID=$!

    # perf stat system-wide
    perf stat -a -x, -o "$RESULTS_DIR/${NAME}_perf_iter${i}.csv" \
        -e dTLB-load-misses,dTLB-store-misses,iTLB-load-misses \
        -e cycles,instructions,page-faults,minor-faults,major-faults \
        sleep $DURATION &
    PERF_PID=$!

    wait $PERF_PID
    wait $VM_PID
    
    sleep 2
done

echo "Data saved to $RESULTS_DIR"
