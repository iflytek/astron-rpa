#!/bin/bash

# Define the target directory and the source policy file
TARGET_DIR="/etc/opt/chrome/policies/managed"
SOURCE_FILE="policy.json"

# Check if the target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    # Create the target directory if it does not exist
    sudo mkdir -p "$TARGET_DIR"
    echo "Directory '$TARGET_DIR' has been created."
fi

# Attempt to copy the policy.json file to the target directory
if ! sudo cp "$SOURCE_FILE" "$TARGET_DIR"; then
    echo "Failed to copy $SOURCE_FILE to $TARGET_DIR. Please check your permissions."
else
    echo "$SOURCE_FILE has been copied to $TARGET_DIR successfully."
fi