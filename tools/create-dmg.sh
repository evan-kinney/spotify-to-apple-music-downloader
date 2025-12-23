#!/bin/bash

# Script to create a DMG installer for Spotify to Apple Music Downloader
# Usage: ./tools/create-dmg.sh

set -e  # Exit on error

echo "Creating DMG installer..."

# Create a temporary directory for DMG contents
mkdir -p tmp

# Copy the app to the temporary directory
cp -R "dist/Spotify to Apple Music Downloader.app" tmp/

# Create a symbolic link to Applications folder
ln -s /Applications tmp/Applications

# Copy background image to a hidden folder
mkdir -p tmp/.background
cp images/background.png tmp/.background/

# Create a temporary DMG
hdiutil create -volname "Spotify to Apple Music Downloader" \
  -srcfolder tmp \
  -ov -format UDRW \
  temp.dmg

# Mount the DMG
echo "Mounting DMG..."
MOUNT_OUTPUT=$(hdiutil attach temp.dmg -nobrowse | grep "/Volumes/")
MOUNT_DIR=$(echo "$MOUNT_OUTPUT" | sed 's/.*\(\/Volumes\/.*\)/\1/')

# Wait for mount
sleep 2

if [ -z "$MOUNT_DIR" ] || [ ! -d "$MOUNT_DIR" ]; then
    echo "Error: DMG did not mount successfully"
    echo "Checking /Volumes..."
    ls -la /Volumes/
    exit 1
fi

echo "DMG mounted successfully at: $MOUNT_DIR"

# Extract the disk name from the mount directory
DISK_NAME=$(basename "$MOUNT_DIR")

# Set DMG window properties with background image
echo "Setting DMG window properties..."
osascript <<APPLESCRIPT
tell application "Finder"
    tell disk "$DISK_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set bounds of container window to {100, 100, 612, 454}
        set arrangement of icon view options of container window to not arranged
        set icon size of icon view options of container window to 64
        set position of item "Spotify to Apple Music Downloader.app" of container window to {111, 136}
        set position of item "Applications" of container window to {401, 136}
        set background picture of icon view options of container window to file ".background:background.png"
        update without registering applications
        delay 2
        close
    end tell
end tell
APPLESCRIPT

echo "Unmounting DMG..."
# Unmount the DMG
hdiutil detach "$MOUNT_DIR" -force
sleep 2

echo "Converting to compressed DMG..."
# Convert to compressed DMG
hdiutil convert temp.dmg -format UDZO -o "Spotify-to-Apple-Music-Downloader.dmg"

# Clean up
rm -f temp.dmg
rm -rf tmp

echo "✅ DMG created: Spotify-to-Apple-Music-Downloader.dmg"
