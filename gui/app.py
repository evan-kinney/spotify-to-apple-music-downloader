"""
Main GUI application window
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import subprocess
import webbrowser
from pathlib import Path
from downloader.spotify_downloader import SpotifyDownloader
from apple_music.importer import AppleMusicImporter


class MusicDownloaderApp:
    """Main application window for the Music Downloader"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Spotify to Apple Music Downloader")
        self.root.geometry("700x400")
        self.root.resizable(True, True)
        
        # Create downloads directory
        self.downloads_dir = Path.home() / "Music" / "Spotify Downloads"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.downloader = SpotifyDownloader(self.downloads_dir)
        self.importer = AppleMusicImporter()
        
        self.is_downloading = False
        self.logs_visible = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Spotify to Apple Music Downloader",
            font=("Helvetica", 18, "bold"),
            pady=20
        )
        title_label.grid(row=0, column=0, sticky="ew")
        
        # URL Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Spotify URL", padding=10)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(input_frame, font=("Helvetica", 12))
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.url_entry.bind('<Return>', lambda e: self.start_download())
        
        self.open_spotify_btn = ttk.Button(
            input_frame,
            text="Open Spotify",
            command=self.open_spotify
        )
        self.open_spotify_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.download_btn = ttk.Button(
            input_frame,
            text="Download",
            command=self.start_download
        )
        self.download_btn.grid(row=0, column=2)
        
        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=10)
        options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.import_to_apple_music = tk.BooleanVar(value=True)
        import_checkbox = ttk.Checkbutton(
            options_frame,
            text="Import to Apple Music after download",
            variable=self.import_to_apple_music
        )
        import_checkbox.grid(row=0, column=0, sticky="w")
        
        self.overwrite_existing = tk.BooleanVar(value=False)
        overwrite_checkbox = ttk.Checkbutton(
            options_frame,
            text="Re-download if file already exists",
            variable=self.overwrite_existing
        )
        overwrite_checkbox.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        progress_frame.grid_columnconfigure(0, weight=1)
        progress_frame.grid_rowconfigure(2, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Toggle logs button
        self.toggle_logs_btn = ttk.Button(
            progress_frame,
            text="Show Logs",
            command=self.toggle_logs
        )
        self.toggle_logs_btn.grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            progress_frame,
            height=15,
            font=("Courier", 10),
            state='disabled',
            wrap=tk.WORD
        )
        self.log_text.grid(row=2, column=0, sticky="nsew")
        self.log_text.grid_remove()  # Hide logs by default
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5
        )
        self.status_label.grid(row=4, column=0, sticky="ew")
    
    def log(self, message):
        """Add a message to the log"""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
    
    def update_status(self, message):
        """Update the status bar"""
        self.status_label.config(text=message)
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def toggle_logs(self):
        """Toggle the visibility of the log text area"""
        if self.logs_visible:
            # Hide logs
            self.log_text.grid_remove()
            self.toggle_logs_btn.config(text="Show Logs")
            self.logs_visible = False
            # Make window smaller when logs are hidden
            self.root.geometry("700x400")
        else:
            # Show logs
            self.log_text.grid()
            self.toggle_logs_btn.config(text="Hide Logs")
            self.logs_visible = True
            # Restore window size when logs are shown
            self.root.geometry("700x600")
    
    def open_spotify(self):
        """Open Spotify app or web player"""
        try:
            # Try to open the Spotify desktop app on macOS
            result = subprocess.run(
                ['open', '-a', 'Spotify'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("Opened Spotify desktop app")
                self.update_status("Opened Spotify desktop app")
            else:
                # If the app is not installed, open the web player
                webbrowser.open('https://open.spotify.com')
                self.log("Opened Spotify web player")
                self.update_status("Opened Spotify web player")
        except Exception as e:
            # Fallback to web player if something goes wrong
            try:
                webbrowser.open('https://open.spotify.com')
                self.log("Opened Spotify web player")
                self.update_status("Opened Spotify web player")
            except Exception as web_error:
                self.log(f"Failed to open Spotify: {str(web_error)}")
                messagebox.showerror("Error", f"Failed to open Spotify: {str(web_error)}")
    
    def start_download(self):
        """Start the download process in a separate thread"""
        if self.is_downloading:
            messagebox.showwarning("In Progress", "A download is already in progress!")
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a Spotify URL!")
            return
        
        # Validate URL
        if "spotify.com" not in url:
            messagebox.showerror("Error", "Please enter a valid Spotify URL!")
            return
        
        # Clear log
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
        # Set initial progress
        self.update_progress(5)
        
        # Disable download button
        self.download_btn.config(state='disabled')
        self.is_downloading = True
        
        # Start download in a separate thread
        thread = threading.Thread(target=self._download_worker, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _download_worker(self, url):
        """Worker function to download and import music"""
        try:
            self.update_status("Downloading...")
            self.update_progress(10)
            self.log(f"Starting download from: {url}")
            
            # Download songs
            downloaded_files = self.downloader.download(
                url,
                progress_callback=self._download_progress_callback,
                overwrite=self.overwrite_existing.get()
            )
            
            if not downloaded_files:
                self.log("No files were downloaded!")
                messagebox.showerror("Error", "No files were downloaded!")
                return
            
            self.log(f"\nSuccessfully downloaded {len(downloaded_files)} file(s)")
            
            # Import to Apple Music if enabled
            if self.import_to_apple_music.get():
                self.update_status("Importing to Apple Music...")
                self.log("\nImporting to Apple Music...")
                
                success_count = 0
                for i, file_path in enumerate(downloaded_files):
                    try:
                        self.log(f"Importing: {file_path.name}")
                        self.importer.import_file(file_path)
                        success_count += 1
                        
                        # Update progress
                        progress = 50 + (50 * (i + 1) / len(downloaded_files))
                        self.update_progress(progress)
                    except Exception as e:
                        self.log(f"Failed to import {file_path.name}: {str(e)}")
                
                self.log(f"\nImported {success_count}/{len(downloaded_files)} file(s) to Apple Music")
            
            self.update_progress(100)
            self.update_status("Complete!")
            messagebox.showinfo("Success", f"Successfully processed {len(downloaded_files)} song(s)!")
            
            # Clear the URL field after successful completion
            self.url_entry.delete(0, tk.END)
            
        except Exception as e:
            self.log(f"\nError: {str(e)}")
            self.update_status("Error!")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Re-enable download button
            self.download_btn.config(state='normal')
            self.is_downloading = False
    
    def _download_progress_callback(self, current, total, message=None):
        """Callback for download progress updates"""
        if message:
            self.log(message)
        
        if total > 0:
            # First 50% is for downloading
            progress = (current / total) * 50
            self.update_progress(progress)
