#!/bin/bash

# Define source and destination paths
SOURCE_DIR="/path/to/folders"
DEST_DIR="/path/to/newfolders"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR does not exist."
    exit 1
fi

# Create destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    echo "Creating destination directory: $DEST_DIR"
    mkdir -p "$DEST_DIR"
fi

# Loop through each folder in the source directory
for folder in "$SOURCE_DIR"/*/; do
    # Skip if no folders found
    [ -e "$folder" ] || continue
    
    # Remove trailing slash and get just the folder name
    folder_name=$(basename "$folder")
    
    # Define the new folder path
    new_folder_path="$DEST_DIR/$folder_name"
    
    # Check if folder already exists in destination
    if [ ! -d "$new_folder_path" ]; then
        # Create the folder in destination
        echo "Creating folder: $new_folder_path"
        mkdir -p "$new_folder_path"
        
        # Set ownership to name.surname:name.surname
        echo "Setting ownership to $folder_name:$folder_name for $folder_name"
        chown "$folder_name:$folder_name" "$new_folder_path"
        
        # Set permissions to 644
        chmod 700 "$new_folder_path"
        
        echo "Successfully created and configured: $folder_name"
    else
        echo "Skipping $folder_name - folder already exists in destination"
    fi
done

echo "Folder recreation completed."
