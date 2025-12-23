#!/usr/bin/env python3
"""
Wrapper script to run spotdl with proper asyncio event loop setup.
This is needed when running spotdl from a bundled macOS app.
"""

import sys
import os
import asyncio
from pathlib import Path
import subprocess

# Set up event loop for the main thread before importing spotdl
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    # No event loop in current thread, create one
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Find and add ffmpeg path if running in a bundle
# Check if we're in an app bundle by looking at the path
script_path = Path(__file__).resolve()
in_app_bundle = '.app/Contents/Resources' in str(script_path)

if in_app_bundle:
    # Running in a bundle
    # Navigate from the script location to the Resources directory
    resources_dir = script_path.parent
    while resources_dir.name != 'Resources' and resources_dir.parent != resources_dir:
        resources_dir = resources_dir.parent

    bundled_ffmpeg = resources_dir / 'bin' / 'ffmpeg'

    print(f"[DEBUG] Running in app bundle", file=sys.stderr)
    print(f"[DEBUG] Script path: {script_path}", file=sys.stderr)
    print(f"[DEBUG] Resources dir: {resources_dir}", file=sys.stderr)
    print(f"[DEBUG] Bundled ffmpeg candidate: {bundled_ffmpeg}", file=sys.stderr)

    chosen_ffmpeg = None

    # If bundled ffmpeg exists, test it
    if bundled_ffmpeg.exists():
        try:
            # Ensure executable
            os.chmod(bundled_ffmpeg, 0o755)
        except Exception as exc:
            print(f"[DEBUG] Failed to chmod bundled ffmpeg: {exc}", file=sys.stderr)

        print(f"[DEBUG] Testing bundled ffmpeg at: {bundled_ffmpeg}", file=sys.stderr)
        try:
            test = subprocess.run(
                [str(bundled_ffmpeg), '-version'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            print(f"[DEBUG] bundled ffmpeg returncode: {test.returncode}", file=sys.stderr)
            if test.returncode == 0:
                chosen_ffmpeg = bundled_ffmpeg
                print(f"[DEBUG] Bundled ffmpeg works", file=sys.stderr)
            else:
                print(f"[DEBUG] Bundled ffmpeg failed: {test.stderr or test.stdout}", file=sys.stderr)
        except Exception as exc:
            print(f"[DEBUG] Error running bundled ffmpeg: {exc}", file=sys.stderr)

    # If bundled not usable, try common system locations for ffmpeg
    if chosen_ffmpeg is None:
        for candidate in ['/opt/homebrew/bin/ffmpeg', '/usr/local/bin/ffmpeg', '/usr/bin/ffmpeg']:
            print(f"[DEBUG] Checking system ffmpeg: {candidate}", file=sys.stderr)
            try:
                test = subprocess.run(
                    [candidate, '-version'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
                if test.returncode == 0:
                    chosen_ffmpeg = Path(candidate)
                    print(f"[DEBUG] Found working system ffmpeg: {candidate}", file=sys.stderr)
                    break
                else:
                    print(f"[DEBUG] System ffmpeg at {candidate} failed: {test.stderr or test.stdout}", file=sys.stderr)
            except FileNotFoundError:
                print(f"[DEBUG] ffmpeg not found at {candidate}", file=sys.stderr)
            except Exception as exc:
                print(f"[DEBUG] Error testing ffmpeg at {candidate}: {exc}", file=sys.stderr)

    # If we found any ffmpeg, use it. Otherwise, fall back to bundled path with ignore flag.
    if chosen_ffmpeg is not None:
        ffmpeg_path = chosen_ffmpeg
        print(f"[DEBUG] Using ffmpeg: {ffmpeg_path}", file=sys.stderr)
        if '--ffmpeg' not in sys.argv and '-f' not in sys.argv:
            sys.argv.extend(['--ffmpeg', str(ffmpeg_path)])
    else:
        # fall back to bundled path if it exists, otherwise let spotdl report missing ffmpeg
        if bundled_ffmpeg.exists():
            print(f"[DEBUG] Falling back to bundled ffmpeg (unverified): {bundled_ffmpeg}", file=sys.stderr)
            if '--ffmpeg' not in sys.argv and '-f' not in sys.argv:
                sys.argv.extend(['--ffmpeg', str(bundled_ffmpeg)])
            if '--ignore-ffmpeg-version' not in sys.argv:
                sys.argv.append('--ignore-ffmpeg-version')
        else:
            print(f"[DEBUG] No ffmpeg available in bundle or system paths", file=sys.stderr)
            # let spotdl handle the missing ffmpeg error

# Now import and run spotdl
from spotdl.console import console_entry_point

if __name__ == "__main__":
    console_entry_point()
