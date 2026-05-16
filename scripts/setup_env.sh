#!/bin/bash
# Master setup script. This script requires sudo.

# 1. Update Nginx Configuration for Phase 1
echo "=== Restarting Nginx with new configurations ==="
if [ -f "/tmp/nginx_default.conf" ]; then
    sudo cp /tmp/nginx_default.conf /etc/nginx/sites-available/default
    sudo systemctl daemon-reload
    sudo systemctl restart nginx
    echo "Nginx configured successfully with sendfile on."
else
    echo "Warning: /tmp/nginx_default.conf not found. Nginx config unchanged."
fi

# 2. Install Matplotlib for Phase 5 plotting
echo "=== Installing Python Matplotlib for Phase 5 ==="
sudo apt-get update
sudo apt-get install python3-matplotlib -y

echo "=== System Setup Complete ==="
