#!/bin/bash
set -e

# Define directories
DATA_DIR="/app/data"
SCENES_DIR="/app/scenes"
DEFAULTS_DIR="/app/defaults/scenes"

echo "Initializing container..."

# 1. Fix Permissions (The user's specific request)
# Since we run as root, this should allow writing to the mounted host volumes.
echo "Fixing permissions for $DATA_DIR and $SCENES_DIR..."
chmod -R 777 "$DATA_DIR" 2>/dev/null || true
chmod -R 777 "$SCENES_DIR" 2>/dev/null || true

# 2. Restore Default Scenes if missing
# When mounting a volume, the image's original content in that folder is hidden.
# We copy it back from our backup location if the destination is empty.
if [ -d "$DEFAULTS_DIR" ]; then
    # Check if scripts dir is empty or doesn't exist
    if [ ! -d "$SCENES_DIR/scripts" ] || [ -z "$(ls -A $SCENES_DIR/scripts 2>/dev/null)" ]; then
        echo "Populating scripts from defaults..."
        mkdir -p "$SCENES_DIR/scripts"
        cp -rn "$DEFAULTS_DIR/scripts/." "$SCENES_DIR/scripts/"
        # Ensure permissions on copied files
        chmod -R 777 "$SCENES_DIR/scripts"
    fi
    
    # Check if clips dir is empty or doesn't exist
    if [ ! -d "$SCENES_DIR/clips" ] || [ -z "$(ls -A $SCENES_DIR/clips 2>/dev/null)" ]; then
        echo "Populating clips from defaults..."
        mkdir -p "$SCENES_DIR/clips"
        cp -rn "$DEFAULTS_DIR/clips/." "$SCENES_DIR/clips/"
        chmod -R 777 "$SCENES_DIR/clips"
    fi
fi

# 3. Execute the passed command (CMD from Dockerfile)
echo "Starting application..."
exec "$@"
