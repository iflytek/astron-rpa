#!/bin/bash

# macOS Chrome Extension Policy Installer

POLICY_DIR="/Library/Application Support/Google/Chrome/policies/managed"
POLICY_FILE="policy.json"

echo "Installing Chrome extension policy for macOS..."

# Create policy directory if not exists
if [ ! -d "$POLICY_DIR" ]; then
    echo "Creating policy directory..."
    sudo mkdir -p "$POLICY_DIR"
fi

# Copy policy file
echo "Copying policy file..."
sudo cp "$POLICY_FILE" "$POLICY_DIR/"

if [ $? -eq 0 ]; then
    echo "Policy installed successfully!"
    echo "Please restart Chrome for the changes to take effect."
else
    echo "Failed to install policy. Please check permissions."
    exit 1
fi
