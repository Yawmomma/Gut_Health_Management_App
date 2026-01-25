#!/bin/bash
set -e

# Directory paths
INSTANCE_DIR="/app/instance"
INITIAL_DB="/app/initial_data/gut_health.db"
TARGET_DB="${INSTANCE_DIR}/gut_health.db"

# Ensure instance directory exists
mkdir -p "$INSTANCE_DIR"

# If database doesn't exist in volume, copy the initial one
if [ ! -f "$TARGET_DB" ]; then
    echo "No database found in volume. Copying initial database..."
    if [ -f "$INITIAL_DB" ]; then
        cp "$INITIAL_DB" "$TARGET_DB"
        echo "Initial database copied successfully."
    else
        echo "Warning: No initial database found at $INITIAL_DB"
        echo "A new empty database will be created on first run."
    fi
else
    echo "Existing database found in volume. Using existing data."
fi

# Execute the main command
exec "$@"
