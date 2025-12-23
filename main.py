#!/usr/bin/env python3
"""
Spotify to Apple Music Downloader
Main application entry point
"""

import tkinter as tk
from gui.app import MusicDownloaderApp


def main():
    """Initialize and run the application"""
    root = tk.Tk()
    app = MusicDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
