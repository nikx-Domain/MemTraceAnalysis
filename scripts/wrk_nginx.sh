#!/bin/bash
# Usage: ./wrk_nginx.sh <duration>

DURATION=${1:-10s}
CONNECTIONS=100
THREADS=4
URL="http://localhost/test_data.bin"

echo "=== Starting Nginx wrk Load Test ==="
echo "Target: $URL"
echo "Duration: $DURATION"
echo "Threads: $THREADS, Connections: $CONNECTIONS"
echo "--------------------------------"

wrk -t$THREADS -c$CONNECTIONS -d$DURATION $URL
echo "=== Done ==="
