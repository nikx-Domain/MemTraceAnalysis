#!/bin/bash
# Description: Sets all CPU scaling governors to performance mode

echo "Setting CPU scaling governors to 'performance'..."
for gov in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [ -f "$gov" ]; then
        echo performance > "$gov"
        echo "Set $gov"
    fi
done
echo "Done."
