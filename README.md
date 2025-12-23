# <img src="images/AppIcon.png" width="25"/> Spotify to Apple Music Downloader

A Python application that downloads songs from Spotify and imports them into Apple Music on macOS.

## Features

- Download individual songs, albums, or playlists from Spotify
- Automatically import downloaded music to Apple Music
- GUI interface with real-time progress tracking
- High-quality MP3 downloads (320kbps)
- Preserves metadata including artist, album, and cover art

## Requirements

- macOS 10.13 or later
- Python 3.8+
- FFmpeg
- Active internet connection

## Installation

### Using the Pre-built App (Recommended)

1. Download the latest DMG from [Releases](https://github.com/evan-kinney/music-downloader/releases)
2. Open the DMG file
3. Drag "Spotify to Apple Music Downloader.app" to your Applications folder
4. Install FFmpeg:

   ```shell
   brew install ffmpeg
   ```

5. Launch the app from Applications

### From Source

1. Clone the repository:

   ```shell
   git clone https://github.com/evan-kinney/music-downloader.git
   cd music-downloader
   ```

2. Install FFmpeg:

   ```shell
   brew install ffmpeg
   ```

3. Install Python dependencies:

   ```shell
   pip install -r requirements.txt
   ```

4. Run the application:

   ```shell
   python main.py
   ```

## Usage

1. Launch the application
2. Paste a Spotify URL into the text field
   - Song: `https://open.spotify.com/track/...`
   - Album: `https://open.spotify.com/album/...`
   - Playlist: `https://open.spotify.com/playlist/...`
3. Choose whether to import to Apple Music (enabled by default)
4. Click "Download" and monitor the progress
5. Downloaded files are saved to `~/Music/Spotify Downloads/`

## Building from Source

### Build the macOS App

```shell
python setup.py py2app
```

The app will be created at `Spotify to Apple Music Downloader.app`. You can open the app by running:

```shell
open "dist/Spotify to Apple Music Downloader.app"
```

### Create a DMG Installer

After building the app, you can create a DMG installer with a background image showing the drag-and-drop installation:

```shell
./tools/create-dmg.sh
```

The DMG file will be created in the current directory. When users open it, they'll see:

- The app icon on the left
- A green arrow with "Drag to install" text
- The Applications folder shortcut on the right

## How It Works

The application uses [spotdl](https://github.com/spotDL/spotify-downloader) to download songs from Spotify URLs. It fetches metadata from Spotify and downloads audio from YouTube Music, then uses AppleScript to import the files into Apple Music with all metadata intact.

## Troubleshooting

### "spotdl not found" error

Install spotdl:

```shell
pip install spotdl
```

### "FFmpeg not found" error

Install FFmpeg using Homebrew:

```shell
brew install ffmpeg
```

### Files already downloaded

The application detects existing files and will skip re-downloading by default. Enable "Re-download if file already exists" to force a fresh download.

### Apple Music import not working

- Ensure you're running on macOS
- Apple Music must be installed
- Grant necessary permissions when prompted

## Project Structure

```text
music-downloader/
├── main.py                      # Application entry point
├── gui/
│   └── app.py                   # Main GUI window
├── downloader/
│   └── spotify_downloader.py    # Spotify download logic
├── apple_music/
│   └── importer.py              # Apple Music integration
├── images/
│   ├── AppIcon.icns             # macOS app icon
│   ├── AppIcon.png              # App icon (PNG format)
│   └── background.png           # DMG background image
├── tools/
│   └── create-dmg.sh            # DMG creation script
├── requirements.txt             # Python dependencies
├── setup.py                     # py2app configuration
└── README.md
```

## Development

### Commit Message Format

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases:

- `feat:` New feature (minor version bump)
- `fix:` Bug fix (patch version bump)
- `docs:` Documentation changes
- `chore:` Maintenance tasks
- `BREAKING CHANGE:` Breaking change (major version bump)

### Running Tests

```shell
python -m pytest
```

## License

See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! If you'd like to contribute, please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## Disclaimer

This project is for educational purposes only. Please respect copyright laws and Spotify's terms of service. Only download music you have the rights to download.
