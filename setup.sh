#!/bin/bash
mkdir -p /tmp/telecaller_dashboard/data
mkdir -p /tmp/telecaller_dashboard/logs
mkdir -p /tmp/telecaller_dashboard/config

# Copy any initial data files if they exist
if [ -d "data" ]; then
    cp -r data/* /tmp/telecaller_dashboard/data/ 2>/dev/null || true
fi

echo "✅ Setup complete - using /tmp/telecaller_dashboard for writable storage"