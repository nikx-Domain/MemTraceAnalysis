#!/bin/bash
# Description: Drop OS page cache to simulate "cold" environments.

echo "Syncing file system..."
sync
echo "Dropping caches..."
echo 3 > /proc/sys/vm/drop_caches
echo "Done."
