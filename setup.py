"""
Setup script for building macOS application with py2app
"""

from setuptools import setup
import shutil
import os

# Copy ffmpeg to the project directory if it exists
ffmpeg_path = shutil.which('ffmpeg')
if ffmpeg_path:
    # Remove existing copy if it exists (it might be read-only)
    if os.path.exists('ffmpeg'):
        os.chmod('ffmpeg', 0o644)  # Make it writable
        os.remove('ffmpeg')
    shutil.copy2(ffmpeg_path, 'ffmpeg')
    os.chmod('ffmpeg', 0o755)  # Make it executable
    print(f"Copied ffmpeg from {ffmpeg_path}")

APP = ['main.py']
DATA_FILES = [
    ('', ['spotdl_wrapper.py', 'run_spotdl.py']),
]

# Add ffmpeg if it was copied
if os.path.exists('ffmpeg'):
    DATA_FILES.append(('bin', ['ffmpeg']))
OPTIONS = {
    'argv_emulation': False,
    'packages': [
        'tkinter',
        'mutagen',
        'asyncio',
        'concurrent',
        'spotdl',
        'charset_normalizer',
        'yt_dlp',
        'ytmusicapi',
        'platformdirs',
        'rapidfuzz',
        'spotipy',
        'bs4',
        'requests',
    ],
    'includes': [
        'gui.app',
        'downloader.spotify_downloader',
        'apple_music.importer',
        'http.cookies',
        'http.cookiejar',
    ],
    'excludes': [
        'setuptools',
        'distutils',
        'test',
        'unittest',
    ],
    'strip': False,  # Don't strip to preserve all symbols
    'iconfile': 'images/AppIcon.icns',  # Custom app icon
    'plist': {
        'CFBundleName': 'Spotify to Apple Music Downloader',
        'CFBundleDisplayName': 'Spotify to Apple Music Downloader',
        'CFBundleGetInfoString': 'Download Spotify songs and import to Apple Music',
        'CFBundleIdentifier': 'com.evankinney.musicdownloader',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 Evan Kinney',
        'LSMinimumSystemVersion': '10.13',
    }
}

setup(
    name='Spotify to Apple Music Downloader',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
