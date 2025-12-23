#!/usr/bin/env python3
"""
Wrapper script to run spotdl with proper asyncio event loop
This is called as a subprocess to avoid event loop conflicts
"""

import sys
import asyncio
from spotdl.console import console_entry_point

if __name__ == "__main__":
    # Ensure we have an event loop for asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Call spotdl's main entry point
    sys.exit(console_entry_point())
