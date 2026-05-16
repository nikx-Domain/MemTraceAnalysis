#!/bin/bash
# YCSB Workload configuration for Phase 2 random access
# This will write ~1-4GB worth of keys and then run random reads against them.
# Sizes can be adjusted below.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
YCSB_BIN="$DIR/../bin/ycsb/bin/ycsb.sh"
RECORD_COUNT=1000000 # 1 million records * ~1KB data = ~1GB. Set to 4000000 for 4GB.
OPERATION_COUNT=1000000

echo "=== Loading Data into Redis ==="
$YCSB_BIN load redis -s -P "$DIR/../bin/ycsb/workloads/workloada" \
    -p "redis.host=127.0.0.1" -p "redis.port=6379" \
    -p "recordcount=$RECORD_COUNT"

echo "=== Running Workload A against Redis ==="
$YCSB_BIN run redis -s -P "$DIR/../bin/ycsb/workloads/workloada" \
    -p "redis.host=127.0.0.1" -p "redis.port=6379" \
    -p "operationcount=$OPERATION_COUNT" -p "recordcount=$RECORD_COUNT" \
    > "$DIR/../data/redis_workload_results.txt"

echo "Workload complete. Results saved in data/redis_workload_results.txt"
