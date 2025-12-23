"""
Apple Music importer using AppleScript
"""

import subprocess
from pathlib import Path
import platform
import os


class AppleMusicImporter:
    """Handles importing music files into Apple Music"""
    
    def __init__(self, delete_after_import: bool = True):
        if platform.system() != "Darwin":
            raise Exception("Apple Music integration is only available on macOS")
        self.delete_after_import = delete_after_import
    
    def import_file(self, file_path: Path) -> bool:
        """
        Import a music file into Apple Music
        
        Args:
            file_path: Path to the music file
        
        Returns:
            True if successful, False otherwise
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Convert to absolute path
        abs_path = file_path.resolve()
        
        # AppleScript to add file to Music
        applescript = f'''
        tell application "Music"
            try
                set theFile to POSIX file "{abs_path}" as alias
                add theFile
                return true
            on error errMsg
                return false
            end try
        end tell
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                check=True
            )
            
            success = "true" in result.stdout.lower()
            
            # Delete the file after successful import if enabled
            if success and self.delete_after_import:
                try:
                    os.remove(abs_path)
                    print(f"Deleted cached file: {abs_path}")
                except Exception as e:
                    print(f"Warning: Could not delete {abs_path}: {e}")
            
            return success
        
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to import to Apple Music: {e.stderr}")
    
    def import_files(self, file_paths: list[Path]) -> dict:
        """
        Import multiple files into Apple Music
        
        Args:
            file_paths: List of file paths to import
        
        Returns:
            Dictionary with 'success' and 'failed' lists
        """
        results = {
            'success': [],
            'failed': []
        }
        
        for file_path in file_paths:
            try:
                if self.import_file(file_path):
                    results['success'].append(file_path)
                else:
                    results['failed'].append(file_path)
            except Exception as e:
                results['failed'].append(file_path)
                print(f"Error importing {file_path}: {e}")
        
        return results
    
    def is_music_running(self) -> bool:
        """Check if Apple Music is running"""
        applescript = '''
        tell application "System Events"
            return (name of processes) contains "Music"
        end tell
        '''
        
        try:
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                check=True
            )
            return "true" in result.stdout.lower()
        except:
            return False
    
    def launch_music(self) -> bool:
        """Launch Apple Music application"""
        applescript = '''
        tell application "Music"
            activate
        end tell
        '''
        
        try:
            subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                check=True
            )
            return True
        except:
            return False
