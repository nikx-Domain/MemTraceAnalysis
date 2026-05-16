#!/bin/bash

NUM_ITERATIONS=10

# 1. Setup Environment
echo "[*] Setting up kernel parameters..."
sudo sysctl -w kernel.perf_event_paranoid=1
sudo sysctl -w vm.nr_hugepages=256

# Create central results directory
mkdir -p results/iterations/

# 2. Run C++ Sequential (Web Server Sim)
echo "[*] Running C++ Sequential - 4KB (Iterations: $NUM_ITERATIONS)..."
for i in $(seq 1 $NUM_ITERATIONS); do
    echo "  Iteration $i/$NUM_ITERATIONS"
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    perf stat -x, -o results/iterations/cpp_4kb_iter${i}.csv -e dTLB-load-misses,page-faults,instructions,cycles ./bin/workload 512 0 0
    sleep 2
done

echo "[*] Running C++ Sequential - 2MB (Iterations: $NUM_ITERATIONS)..."
for i in $(seq 1 $NUM_ITERATIONS); do
    echo "  Iteration $i/$NUM_ITERATIONS"
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    perf stat -x, -o results/iterations/cpp_2mb_iter${i}.csv -e dTLB-load-misses,page-faults,instructions,cycles ./bin/workload 512 0 1
    sleep 2
done

# 3. Run Redis Benchmark (Database Sim)
echo "[*] Running Redis Benchmark - 4KB (Iterations: $NUM_ITERATIONS)..."
for i in $(seq 1 $NUM_ITERATIONS); do
    echo "  Iteration $i/$NUM_ITERATIONS"
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    perf stat -x, -o results/iterations/redis_4kb_iter${i}.csv -e dTLB-load-misses,page-faults,instructions,cycles redis-benchmark -t set,get -n 1000000 > results/iterations/redis_4kb_latency_iter${i}.txt
    sleep 2
done

echo "[*] Running Redis Benchmark - 2MB (Iterations: $NUM_ITERATIONS)..."
for i in $(seq 1 $NUM_ITERATIONS); do
    echo "  Iteration $i/$NUM_ITERATIONS"
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    perf stat -x, -o results/iterations/redis_2mb_iter${i}.csv -e dTLB-load-misses,page-faults,instructions,cycles redis-benchmark -t set,get -n 1000000 > results/iterations/redis_2mb_latency_iter${i}.txt
    sleep 2
done

# 4. Run Nginx Benchmark (Web Server Sim)
echo "[*] Running Nginx Benchmark - 4KB (Iterations: $NUM_ITERATIONS)..."
for i in $(seq 1 $NUM_ITERATIONS); do
    echo "  Iteration $i/$NUM_ITERATIONS"
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    perf stat -x, -o results/iterations/nginx_4kb_iter${i}.csv -e dTLB-load-misses,page-faults,instructions,cycles \
        wrk -t4 -c100 -d10s http://localhost/ > results/iterations/nginx_4kb_latency_iter${i}.txt 2>&1
    sleep 2
done

echo "[*] Running Nginx Benchmark - 2MB (Iterations: $NUM_ITERATIONS)..."
for i in $(seq 1 $NUM_ITERATIONS); do
    echo "  Iteration $i/$NUM_ITERATIONS"
    sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    perf stat -x, -o results/iterations/nginx_2mb_iter${i}.csv -e dTLB-load-misses,page-faults,instructions,cycles \
        wrk -t4 -c100 -d10s http://localhost/ > results/iterations/nginx_2mb_latency_iter${i}.txt 2>&1
    sleep 2
done

echo "[*] All iterations complete!"
echo "Results saved to: results/iterations/"
