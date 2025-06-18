# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Qoosie is a TUI (Text User Interface) YouTube to MP3 converter written in Python. It provides a kawaii-style interface for downloading YouTube videos and converting them to MP3 format with waveform visualization capabilities.

## Architecture

The application is structured as a single-file Python script (`qoozie.py`) with the following key components:

- **Main TUI**: Built using `rich` library for layout management, panels, and progress bars
- **YouTube Download**: Uses `yt-dlp` for video downloading with progress hooks
- **Audio Conversion**: Uses `ffmpeg-python` for format conversion to MP3
- **Waveform Visualization**: Uses `pydub` and `librosa` for audio analysis and ASCII waveform generation
- **Visual Elements**: Uses `pyfiglet` for ASCII art title generation

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv JQSSenv
source JQSSenv/bin/activate  # On Linux/Mac
# JQSSenv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
python qoozie.py
```

### New Waveform Controls
- **w** or **t**: Toggle waveform display in footer
- **h**: Hide waveform display
- **f**: Show full-screen waveform (when download complete)
- **ENTER**: New download (when download complete)
- **ESC**: Quit application

The footer waveform display features:
- High-quality ASCII visualization with Unicode block characters
- Color-coded amplitude representation (green→yellow→red for intensity)
- Automatic mono/stereo detection and display
- Real-time terminal width adaptation
- Efficient caching system for smooth performance
- File information display (duration, sample rate, channels)

### Key Dependencies
- `yt-dlp`: YouTube video downloading
- `ffmpeg-python`: Audio format conversion
- `rich`: TUI components and styling
- `pydub`: Audio file manipulation
- `librosa`: Audio analysis
- `pyfiglet`: ASCII art generation

## Code Architecture Notes

- The main application flow is handled by `maino()` function
- Layout management is done through `casa()` function which creates the TUI structure with dynamic footer sizing
- Download functionality is in `YT_Presta()` with progress hook integration
- Audio conversion is handled by `Mp3fy()` function
- Waveform visualization is provided by `visualize_waveform()` function for full-screen display
- **NEW**: `WaveformManager` class handles high-quality footer waveform display with caching and optimized rendering
- **NEW**: Footer waveform integration with Live rendering system, supporting both mono and stereo display
- The app uses multi-threaded approach with rich's layout system for real-time updates and smooth waveform rendering

## File Structure

- `qoozie.py`: Main application file
- `requirements.txt`: Python dependencies
- `JQSSenv/`: Virtual environment directory
- `README.md`: ASCII art welcome message