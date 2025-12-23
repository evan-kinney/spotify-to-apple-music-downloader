"""
Spotify downloader using spotdl
"""

import subprocess
import json
import os
import sys
import asyncio
from pathlib import Path
from typing import List, Callable, Optional


class SpotifyDownloader:
    """Handles downloading songs from Spotify using spotdl"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download(
        self,
        url: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        overwrite: bool = False
    ) -> List[Path]:
        """
        Download songs from a Spotify URL
        
        Args:
            url: Spotify URL (song, album, or playlist)
            progress_callback: Optional callback function(current, total, message)
            overwrite: If True, re-download even if file exists
        
        Returns:
            List of downloaded file paths
        """
        downloaded_files = []
        
        try:
            # First, get the list of songs
            if progress_callback:
                progress_callback(0, 1, "Fetching song information...")
            
            # Get list of existing files before download
            existing_files = set(self.output_dir.glob("*.*"))
            
            # Use our wrapper script that sets up asyncio event loop properly
            # Find the wrapper script - it's bundled in Resources directory
            if getattr(sys, 'frozen', False):
                # Running in a bundle
                bundle_dir = Path(sys.executable).parent.parent / 'Resources'
                wrapper_script = bundle_dir / 'run_spotdl.py'
            else:
                # Running in development
                wrapper_script = Path(__file__).parent.parent / 'run_spotdl.py'
            
            cmd = [
                sys.executable,
                str(wrapper_script),
                url,
                '--output', str(self.output_dir),
                '--output-format', 'mp3',
                '--download-threads', '4'
            ]
            
            # If overwrite is requested, delete existing files that match this URL
            # This is a workaround since spotdl doesn't have an overwrite flag
            if overwrite and progress_callback:
                progress_callback(0, 1, "Checking for existing files to overwrite...")
            
            if progress_callback:
                progress_callback(0, 1, f"Running: {' '.join(cmd)}")
            
            # Create a clean environment that uses system paths
            # This ensures spotdl uses system Python, not the bundled app's Python
            env = os.environ.copy()
            # Make sure we use the system PATH
            if 'PATH' not in env:
                env['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
            # Set UTF-8 encoding to handle unicode characters
            env['PYTHONIOENCODING'] = 'utf-8'
            env['LC_ALL'] = 'en_US.UTF-8'
            env['LANG'] = 'en_US.UTF-8'
            
            # Run the download process
            # Use subprocess.run with text output to capture everything at once
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters instead of failing
                cwd=str(self.output_dir),
                env=env,
                shell=False
            )
            
            # Log the output
            if progress_callback:
                for line in result.stdout.splitlines():
                    if line.strip():
                        progress_callback(0, 1, line.strip())
                
                # Also log stderr if there's any
                for line in result.stderr.splitlines():
                    if line.strip():
                        progress_callback(0, 1, line.strip())
            
            if result.returncode != 0:
                # Check if it's a module not found error
                if "No module named" in result.stderr or "No module named" in result.stdout:
                    raise ModuleNotFoundError(
                        "spotdl module is not available. This is a bundling issue.\n"
                        "Please report this error to the developer."
                    )
                # Check if it's because files were already downloaded
                elif "already downloaded" in result.stderr.lower() or "already downloaded" in result.stdout.lower():
                    if progress_callback:
                        progress_callback(0, 1, "Files already exist, checking for existing downloads...")
                    # Don't raise an error, just continue to find the files
                else:
                    # Provide more detailed error message
                    error_msg = f"spotdl exited with code {result.returncode}"
                    if result.stderr:
                        error_msg += f"\nError output: {result.stderr}"
                    raise Exception(error_msg)
            
            # Find newly downloaded files
            # Get all files after download
            current_files = set(self.output_dir.glob("*.*"))
            new_files = current_files - existing_files
            
            # Filter to only include music files (exclude cache and other non-music files)
            music_extensions = {'.mp3', '.m4a', '.flac', '.wav', '.ogg', '.opus'}
            
            # If we found new files, filter them
            if new_files:
                downloaded_files = [
                    f for f in new_files 
                    if f.suffix.lower() in music_extensions and not f.name.startswith('.')
                ]
            
            # If no new files or empty list, look for existing music files
            if not downloaded_files:
                # Look for all music files in the directory (sorted by most recent)
                all_music_files = []
                for ext in music_extensions:
                    for file_path in self.output_dir.glob(f"*{ext}"):
                        if not file_path.name.startswith('.'):
                            all_music_files.append(file_path)
                
                # Sort by modification time and take the most recent one(s)
                all_music_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # If we have files, take the most recent one (likely what was just checked)
                if all_music_files:
                    downloaded_files = [all_music_files[0]]
            
            # Sort by modification time (most recent first)
            if downloaded_files:
                downloaded_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if progress_callback:
                progress_callback(
                    len(downloaded_files),
                    len(downloaded_files),
                    f"Download complete! Found {len(downloaded_files)} file(s)"
                )
            
            return downloaded_files
        
        except FileNotFoundError:
            raise Exception(
                "spotdl not found! Please install it with: pip install spotdl\n"
                "You also need FFmpeg installed: brew install ffmpeg"
            )
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        try:
            # Check spotdl
            subprocess.run(
                ['spotdl', '--version'],
                capture_output=True,
                check=True
            )
            
            # Check ffmpeg
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )
            
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
