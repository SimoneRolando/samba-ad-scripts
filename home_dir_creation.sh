#!/bin/bash

# Define source and destination paths
SOURCE_DIR="/mnt/storage/userdirs"
DEST_DIR="/mnt/storage/linuxdirs"
LOG_FILE="/var/log/folder_recreation.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    log_message "ERROR: Source directory $SOURCE_DIR does not exist."
    exit 1
fi

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    log_message "INFO: Creating destination directory: $DEST_DIR"
    mkdir -p "$DEST_DIR" || {
        log_message "ERROR: Failed to create destination directory $DEST_DIR"
        exit 1
    }
fi

# Initialize log file
log_message "Starting folder recreation process"
log_message "Source: $SOURCE_DIR"
log_message "Destination: $DEST_DIR"

# Counter for statistics
success_count=0
skip_count=0
error_count=0

# Loop through each folder in the source directory
for folder in "$SOURCE_DIR"/*/; do
    # Skip if no folders found
    [ -e "$folder" ] || continue
    
    # Remove trailing slash and get just the folder name
    folder_name=$(basename "$folder")
    
    # Check if folder name follows the pattern "name.owner"
    if [[ "$folder_name" =~ ^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$ ]]; then
        # Extract name and owner from folder name
        name=$(echo "$folder_name" | cut -d. -f1)
        owner=$(echo "$folder_name" | cut -d. -f2)
        
        # Create the folder in destination
        new_folder_path="$DEST_DIR/$folder_name"
        
        log_message "PROCESSING: $folder_name -> $new_folder_path"
        
        # Create directory
        if mkdir -p "$new_folder_path" 2>/dev/null; then
            # Set ownership
            if chown "$name:$owner" "$new_folder_path" 2>/dev/null; then
                # Set permissions
                if chmod 644 "$new_folder_path" 2>/dev/null; then
                    log_message "SUCCESS: $folder_name - ownership: $name:$owner, permissions: 644"
                    ((success_count++))
                else
                    log_message "ERROR: Failed to set permissions for $folder_name"
                    ((error_count++))
                fi
            else
                log_message "ERROR: Failed to set ownership for $folder_name"
                ((error_count++))
            fi
        else
            log_message "ERROR: Failed to create directory $new_folder_path"
            ((error_count++))
        fi
    else
        log_message "SKIPPED: $folder_name - does not match pattern 'name.owner'"
        ((skip_count++))
    fi
done

# Print summary
log_message "PROCESS COMPLETED: Success: $success_count, Skipped: $skip_count, Errors: $error_count"
