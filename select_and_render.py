#!/usr/bin/env python3
"""
Interactive script for selecting and rendering World of Warships replay files.

This script scans the replays directory for .wowsreplay files, presents them
to the user in an interactive list, and renders the selected replay using the
existing render module.

Usage:
    python select_and_render.py

Features:
- Lists all .wowsreplay files in the replays/ directory
- Shows file sizes for each replay
- Interactive numbered selection
- Graceful error handling for missing dependencies
- Uses the existing rendering engine

Dependencies:
The script requires the same dependencies as the main renderer:
- numpy
- lxml  
- pycryptodomex
- imageio-ffmpeg
- Pillow
- tqdm

Install with: pip install -r requirements.txt
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def find_replay_files(replay_dir):
    """Find all .wowsreplay files in the given directory."""
    replay_path = Path(replay_dir)
    if not replay_path.exists():
        print(f"Error: Replay directory '{replay_dir}' does not exist.")
        return []
    
    replay_files = list(replay_path.glob("*.wowsreplay"))
    return sorted(replay_files)


def display_replay_menu(replay_files):
    """Display a numbered menu of replay files."""
    print("\nAvailable replay files:")
    print("-" * 50)
    
    for i, replay_file in enumerate(replay_files, 1):
        file_size = replay_file.stat().st_size
        size_mb = file_size / (1024 * 1024)
        print(f"{i:2d}. {replay_file.name} ({size_mb:.1f} MB)")
    
    print("-" * 50)


def get_user_selection(replay_files):
    """Get user's replay selection."""
    while True:
        try:
            choice = input(f"\nSelect a replay file (1-{len(replay_files)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("Exiting...")
                return None
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(replay_files):
                return replay_files[choice_num - 1]
            else:
                print(f"Please enter a number between 1 and {len(replay_files)}")
        
        except ValueError:
            print("Please enter a valid number or 'q' to quit")


def render_replay(replay_file):
    """Render the selected replay file using the existing render module."""
    print(f"\nStarting render of: {replay_file.name}")
    print("=" * 60)
    
    try:
        # Try to use the existing render script via subprocess
        script_path = Path(__file__).parent / "src" / "render.py"
        
        if not script_path.exists():
            print(f"Error: Render script not found at {script_path}")
            return False
        
        # Run the render script as a subprocess
        cmd = [sys.executable, str(script_path), "--replay", str(replay_file)]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
        
        if result.returncode == 0:
            print("Rendering completed successfully!")
            print(result.stdout)
            return True
        else:
            print(f"Rendering failed with return code {result.returncode}")
            if "ModuleNotFoundError" in result.stderr:
                print("\nMissing Dependencies:")
                print("The rendering engine requires additional Python packages.")
                print("Please install them by running:")
                print("  pip install -r requirements.txt")
                print("\nOr install the core dependencies:")
                print("  pip install numpy lxml pycryptodomex imageio-ffmpeg Pillow tqdm")
            else:
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            return False
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the render module is available.")
        return False
    except Exception as e:
        print(f"Error during rendering: {e}")
        return False


def main():
    """Main function to run the interactive replay selection and rendering."""
    print("World of Warships Replay Renderer")
    print("=" * 40)
    
    # Define the replay directory
    script_dir = Path(__file__).parent
    replay_dir = script_dir / "replays"
    
    # Find replay files
    replay_files = find_replay_files(replay_dir)
    
    if not replay_files:
        print(f"No .wowsreplay files found in '{replay_dir}'")
        print("Please add some replay files to the replays directory.")
        return 1
    
    # Display menu and get user selection
    display_replay_menu(replay_files)
    selected_replay = get_user_selection(replay_files)
    
    if selected_replay is None:
        return 0
    
    # Render the selected replay
    success = render_replay(selected_replay)
    
    if success:
        print(f"\nRendering completed successfully!")
        video_path = selected_replay.parent / f"{selected_replay.stem}.mp4"
        print(f"Output video: {video_path}")
    else:
        print("\nRendering failed. Please check the error messages above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)