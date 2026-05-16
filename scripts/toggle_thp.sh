#!/bin/bash
# Usage: ./toggle_thp.sh [always|madvise|never]
MODE=${1:-always}

if [[ "$MODE" != "always" && "$MODE" != "madvise" && "$MODE" != "never" ]]; then
    echo "Invalid mode. Use: always, madvise, or never."
    exit 1
fi

echo "Setting THP mode to: $MODE"
echo $MODE > /sys/kernel/mm/transparent_hugepage/enabled

echo -n "Current THP Mode: "
cat /sys/kernel/mm/transparent_hugepage/enabled
