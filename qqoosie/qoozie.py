"""

QOOSIE es una TUI convertidor de youtube a mp3 glitcheado.
            Gestiona tus descargas en la carpeta de preferencia.
            Hasta 8 pistas de entre tus descargas para samplear y procesar.
            Posibilidad de poder alterar el buffer.

METAS :
        - TUI bonita psyfisoza kawaii yacasi
        - poder guardar tus mp3/wavs en una carpeta destinada
        - crear subcarpeta donde se guardan los audios procesados
        - crear subcarpeta de fadrStems
        * abrir fadr.com automaticamente para que puedas sacar la acapella

        -buen windowing para que los loops cortos no tengan clicks duros
        *ffts para sintesis de esta indole
        *poder tocar cromaticamente los samples
        *buen pitch y timestretch
        *(non realtime processing para tareas demandantes)


"""

import random, os
import sqlite3
import subprocess
from time import sleep, time
import threading
import queue
import sys
import select
import termios
import tty
import yt_dlp
import ffmpeg
import librosa
import numpy as np
import pydub
import pyfiglet
import typer
from rich.console import Console
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
# from rich import print
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
)
from rich.text import Text
from rich.table import Table
from yt_dlp.utils import sanitize_filename

# Activar Consola rich
consola= Console()
# consola.print("[green italic] xd oh si [/green italic]")



def Figlich(msg, coloro, modo, tipox="heart_right"):
    fonfig = pyfiglet.Figlet(font=tipox)
    asciid = fonfig.renderText(msg)

    if modo == "n":
        consola.print(f"[{coloro}]{asciid}[/{coloro}]")
    elif modo == "p":
       consola.print(
            Panel(
                f"[blink][{coloro}]{asciid}[/{coloro}][/blink]",
                title=f"[blink] 🛁  Q q o S s i e 🛁 [/blink]",
                subtitle="OuO yt -> audio O.o",
                border_style="purple",
            )
        )
    elif modo == "pf":
        consola.print(Panel.fit(f"[{coloro}]{asciid}[/{coloro}]", border_style="cyan"))

def visualize_waveform(audio_file, width=80, height=10):
    """Generate bipolar ASCII waveform visualization"""
    try:
        # Load audio with librosa for better processing
        y, sr = librosa.load(audio_file)
        
        # Calculate chunks for visualization
        hop_length = max(1, len(y) // width)
        
        # Get amplitude values for bipolar display
        amplitude_chunks = []
        for i in range(0, len(y), hop_length):
            chunk = y[i:i + hop_length]
            if len(chunk) > 0:
                # Get both positive and negative peaks
                pos_peak = max(chunk) if len(chunk) > 0 else 0
                neg_peak = min(chunk) if len(chunk) > 0 else 0
                amplitude_chunks.append((pos_peak, neg_peak))
        
        # Ensure we have enough chunks
        while len(amplitude_chunks) < width:
            amplitude_chunks.append((0, 0))
        amplitude_chunks = amplitude_chunks[:width]
        
        # Normalize to height
        max_amp = max(max(abs(pos), abs(neg)) for pos, neg in amplitude_chunks) or 1
        center_line = height // 2
        
        # Generate bipolar waveform
        waveform_lines = []
        
        for line_idx in range(height):
            line_str = []
            for pos_amp, neg_amp in amplitude_chunks:
                # Normalize amplitudes
                pos_height = int((pos_amp / max_amp) * center_line)
                neg_height = int((abs(neg_amp) / max_amp) * center_line)
                
                if line_idx < center_line - pos_height:
                    # Above positive wave
                    line_str.append(" ")
                elif line_idx < center_line:
                    # Positive wave area
                    line_str.append("[green]▄[/]")
                elif line_idx == center_line:
                    # Center line
                    line_str.append("[dim white]─[/]")
                elif line_idx <= center_line + neg_height:
                    # Negative wave area  
                    line_str.append("[red]▀[/]")
                else:
                    # Below negative wave
                    line_str.append(" ")
            
            waveform_lines.append("".join(line_str))
        
        # Create waveform panel
        waveform_display = "\n".join(waveform_lines)
        
        waveform_panel = Panel(
            waveform_display,
            title=f"[bold]Bipolar Waveform: {os.path.basename(audio_file)}[/]",
            subtitle=f"[dim]Sample Rate: {sr}Hz • Duration: {len(y)/sr:.2f}s[/]",
            border_style="blue",
        )
        
        consola.print(waveform_panel)
        
    except Exception as e:
        consola.print(Panel(
            f"[red]Waveform generation error: {str(e)}[/]",
            border_style="red"
        ))


class WaveformManager:
    """High-quality waveform generator and display manager for footer integration"""
    
    def __init__(self, max_width=120, max_height=6):
        self.max_width = max_width
        self.max_height = max_height
        self.waveform_cache = {}
        self.current_file = None
        self.waveform_data = None
        self.display_buffer = None
        self.is_stereo = False
        self.sample_rate = 44100
        self.duration = 0
        
        # Enhanced ASCII characters for better resolution
        self.wave_chars = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        self.center_char = '─'
        
        # Color gradients for amplitude visualization
        self.color_map = {
            0: "dim white",
            1: "bright_black", 
            2: "green",
            3: "yellow",
            4: "bright_yellow",
            5: "red",
            6: "bright_red",
            7: "magenta",
            8: "bright_magenta"
        }
    
    def generate_waveform_data(self, audio_file):
        """Generate optimized waveform data for footer display"""
        try:
            # Check cache first
            cache_key = f"{audio_file}_{self.max_width}_{self.max_height}"
            if cache_key in self.waveform_cache:
                return self.waveform_cache[cache_key]
            
            # Load audio with librosa for superior processing
            y, sr = librosa.load(audio_file, sr=None)
            self.current_file = audio_file
            self.sample_rate = sr
            self.duration = len(y) / sr
            
            # Check if stereo
            if len(y.shape) > 1:
                self.is_stereo = True
                y_left = y[0] if y.shape[0] == 2 else y
                y_right = y[1] if y.shape[0] == 2 else y
            else:
                self.is_stereo = False
                y_left = y
                y_right = None
            
            # Generate waveform data
            waveform_data = self._process_audio_channels(y_left, y_right)
            
            # Cache the result
            self.waveform_cache[cache_key] = waveform_data
            self.waveform_data = waveform_data
            
            return waveform_data
            
        except Exception as e:
            return None
    
    def _process_audio_channels(self, left_channel, right_channel=None):
        """Process audio channels into display-ready format"""
        # Calculate optimal hop length for width
        hop_length = max(1, len(left_channel) // self.max_width)
        
        # Process left channel
        left_peaks = self._extract_peaks(left_channel, hop_length)
        
        # Process right channel if stereo
        right_peaks = None
        if right_channel is not None:
            right_peaks = self._extract_peaks(right_channel, hop_length)
        
        return {
            'left': left_peaks,
            'right': right_peaks,
            'is_stereo': right_channel is not None,
            'duration': self.duration,
            'sample_rate': self.sample_rate
        }
    
    def _extract_peaks(self, channel_data, hop_length):
        """Extract amplitude peaks for visualization"""
        peaks = []
        for i in range(0, len(channel_data), hop_length):
            chunk = channel_data[i:i + hop_length]
            if len(chunk) > 0:
                # Get RMS value for better representation
                rms = np.sqrt(np.mean(chunk ** 2))
                # Get peak values
                pos_peak = np.max(chunk) if len(chunk) > 0 else 0
                neg_peak = np.min(chunk) if len(chunk) > 0 else 0
                peaks.append({
                    'rms': rms,
                    'pos': pos_peak,
                    'neg': neg_peak
                })
        
        # Ensure we have enough data points
        while len(peaks) < self.max_width:
            peaks.append({'rms': 0, 'pos': 0, 'neg': 0})
        
        return peaks[:self.max_width]
    
    def render_footer_waveform(self, width, height=6):
        """Render compact waveform for footer display"""
        if not self.waveform_data:
            return self._render_no_waveform()
        
        # Adjust dimensions
        display_width = min(width - 4, self.max_width)  # Account for panel borders
        display_height = min(height, self.max_height)
        
        left_peaks = self.waveform_data['left']
        right_peaks = self.waveform_data.get('right')
        
        if self.waveform_data['is_stereo'] and right_peaks:
            return self._render_stereo_waveform(left_peaks, right_peaks, display_width, display_height)
        else:
            return self._render_mono_waveform(left_peaks, display_width, display_height)
    
    def _render_mono_waveform(self, peaks, width, height):
        """Render mono waveform with enhanced quality"""
        lines = []
        
        # Normalize peaks
        max_rms = max(peak['rms'] for peak in peaks) or 1
        center_line = height // 2
        
        for line_idx in range(height):
            line_chars = []
            for peak in peaks[:width]:
                # Calculate amplitude representation
                rms_norm = peak['rms'] / max_rms
                pos_norm = abs(peak['pos']) / max_rms if max_rms > 0 else 0
                neg_norm = abs(peak['neg']) / max_rms if max_rms > 0 else 0
                
                # Determine character and color based on position
                if line_idx < center_line:
                    # Upper half - positive peaks
                    upper_threshold = (center_line - line_idx) / center_line
                    if pos_norm >= upper_threshold:
                        char_idx = min(8, int(pos_norm * 8))
                        color = self.color_map[char_idx]
                        line_chars.append(f"[{color}]{self.wave_chars[char_idx]}[/]")
                    else:
                        line_chars.append(" ")
                elif line_idx == center_line:
                    # Center line
                    if rms_norm > 0.01:  # Show activity
                        line_chars.append(f"[{self.color_map[2]}]{self.center_char}[/]")
                    else:
                        line_chars.append(f"[dim]{self.center_char}[/]")
                else:
                    # Lower half - negative peaks
                    lower_threshold = (line_idx - center_line) / center_line
                    if neg_norm >= lower_threshold:
                        char_idx = min(8, int(neg_norm * 8))
                        color = self.color_map[char_idx]
                        line_chars.append(f"[{color}]{self.wave_chars[char_idx]}[/]")
                    else:
                        line_chars.append(" ")
            
            lines.append("".join(line_chars))
        
        return "\n".join(lines)
    
    def _render_stereo_waveform(self, left_peaks, right_peaks, width, height):
        """Render stereo waveform with channel separation"""
        lines = []
        
        # Split height for two channels
        channel_height = height // 2
        
        # Normalize both channels together
        all_peaks = left_peaks + right_peaks
        max_rms = max(peak['rms'] for peak in all_peaks) or 1
        
        # Render left channel (top half)
        for line_idx in range(channel_height):
            line_chars = []
            for peak in left_peaks[:width]:
                rms_norm = peak['rms'] / max_rms
                char_idx = min(8, int(rms_norm * 8))
                color = self.color_map[char_idx]
                
                if char_idx > 0:
                    line_chars.append(f"[{color}]L{self.wave_chars[char_idx]}[/]")
                else:
                    line_chars.append("  ")
            lines.append("".join(line_chars))
        
        # Separator line
        separator = f"[dim]{'─' * (width * 2)}[/]"
        lines.append(separator)
        
        # Render right channel (bottom half)
        for line_idx in range(channel_height):
            line_chars = []
            for peak in right_peaks[:width]:
                rms_norm = peak['rms'] / max_rms
                char_idx = min(8, int(rms_norm * 8))
                color = self.color_map[char_idx]
                
                if char_idx > 0:
                    line_chars.append(f"[{color}]R{self.wave_chars[char_idx]}[/]")
                else:
                    line_chars.append("  ")
            lines.append("".join(line_chars))
        
        return "\n".join(lines)
    
    def _render_no_waveform(self):
        """Render placeholder when no waveform data available"""
        return "[dim]No waveform data available[/]"
    
    def get_file_info(self):
        """Get formatted file information for display"""
        if not self.current_file or not self.waveform_data:
            return ""
        
        filename = os.path.basename(self.current_file)
        duration_str = f"{self.duration:.1f}s"
        sr_str = f"{self.sample_rate}Hz"
        stereo_str = "Stereo" if self.waveform_data['is_stereo'] else "Mono"
        
        return f"[bold]{filename}[/] • [cyan]{duration_str}[/] • [yellow]{sr_str}[/] • [magenta]{stereo_str}[/]"

def Mp3fy(input_file, output_file):
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            consola.print(f"[red]Input file not found: {input_file}[/red]")
            return False

        # Use ffmpeg-python API
        (
            ffmpeg
            .input(input_file)
            .output(output_file,
                    acodec='libmp3lame',
                    audio_bitrate='192k',
                    ar=44100,
                    vn=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )

        consola.print(f"[green]✓ Converted to MP3: {output_file}[/green]")
        return True
    except ffmpeg.Error as e:
        consola.print(f"[red]FFmpeg conversion failed: {e.stderr.decode()}[/red]")
        return False
    except Exception as e:
        consola.print(f"[red]Unexpected error: {str(e)}[/red]")
        return False



def casa(waveform_active=False, waveform_height=6):
    """Responsive layout with dynamic sizing to prevent scrolling issues"""
    layout = Layout()
    
    # Get terminal dimensions for responsive design
    terminal_height = consola.size.height
    terminal_width = consola.size.width
    
    # Calculate responsive sizes
    header_size = max(2, min(3, terminal_height // 12))  # 2-3 lines based on terminal
    footer_base = max(2, min(3, terminal_height // 10))  # Responsive base footer
    footer_size = footer_base if not waveform_active else max(footer_base, waveform_height + 3)
    
    # Ensure we don't exceed 70% of terminal height for fixed elements
    max_fixed = int(terminal_height * 0.7)
    if header_size + footer_size > max_fixed:
        footer_size = max(2, max_fixed - header_size)
    
    # Use responsive sizes to prevent scrolling
    layout.split(
        Layout(name="header", minimum_size=header_size),
        Layout(name="main"),
        Layout(name="footer", minimum_size=footer_base, size=footer_size),
    )
    
    # Responsive sidebar sizing
    sidebar_min = max(16, min(25, terminal_width // 5))  # 16-25 chars, max 20% width
    layout["main"].split_row(
        Layout(name="content", ratio=3),
        Layout(name="sidebar", minimum_size=sidebar_min, ratio=1)
    )

    # Adaptive header content based on available space
    if header_size >= 3:
        header_content = Align.center(
            Text.from_markup(
                "[bold blink]🎵 Qoossie Audio Downloader 🎵[/]\n"
                "[italic cyan]YouTube → MP3/WAV Converter[/]"
            )
        )
    else:
        header_content = Align.center(
            Text.from_markup("[bold blink]🎵 Qoossie 🎵[/]")
        )
    
    layout["header"].update(
        Panel(
            header_content,
            border_style="green"
        )
    )

    # Dynamic footer based on waveform status
    if waveform_active:
        # Split footer for controls and waveform
        layout["footer"].split(
            Layout(name="controls", size=3),
            Layout(name="waveform", size=waveform_height + 1)
        )
        
        # Compact controls panel
        controls_text = "[yellow][bold]ESC[/] quit • [bold]ENTER[/] new • [bold]t[/] toggle • [bold]h[/] hide[/yellow]"
        layout["footer"]["controls"].update(
            Panel(
                controls_text,
                border_style="yellow"
            )
        )
        
        # Waveform panel (will be updated by QoosieApp)
        layout["footer"]["waveform"].update(
            Panel(
                "[dim]Waveform loading...[/]",
                title="[bold]Audio Waveform[/]",
                border_style="cyan"
            )
        )
    else:
        # Compact default footer
        controls_text = "[yellow][bold]ESC[/] quit • [bold]ENTER[/] submit • [bold]w[/] waveform[/yellow]"
        layout["footer"].update(
            Panel(
                controls_text,
                border_style="yellow"
            )
        )

    return layout


class QoosieApp:
    """Enhanced TUI application with Live rendering and threading"""
    
    def __init__(self):
        self.waveform_active = False
        self.waveform_height = 6
        self.layout = casa(self.waveform_active, self.waveform_height)
        self.current_status = "idle"
        self.input_buffer = ""
        self.input_active = True
        self.live = None
        self.download_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.download_thread = None
        self.running = True
        self.layout_lock = threading.Lock()
        
        # Waveform management
        self.waveform_manager = WaveformManager(max_width=120, max_height=self.waveform_height)
        self.current_file = None
        self.waveform_update_thread = None
        self.waveform_queue = queue.Queue()
        
        # Initialize content
        self.update_input_display()
        
    def update_layout(self, section, content):
        """Thread-safe layout updates"""
        with self.layout_lock:
            if self.layout:
                self.layout[section].update(content)
    
    def toggle_waveform_display(self):
        """Toggle waveform display in footer"""
        self.waveform_active = not self.waveform_active
        
        # Recreate layout with new waveform status
        with self.layout_lock:
            self.layout = casa(self.waveform_active, self.waveform_height)
            
            # Restore current content based on status
            if self.current_status == "idle":
                self.update_input_display()
            elif self.current_status == "complete" and self.current_file:
                if self.waveform_active:
                    self.start_waveform_generation(self.current_file)
                self.update_completion_display()
    
    def start_waveform_generation(self, audio_file):
        """Start waveform generation in background thread"""
        if not self.waveform_active:
            return
            
        def generate_waveform():
            try:
                # Update footer to show loading
                if self.waveform_active:
                    self.update_layout("footer.waveform", Panel(
                        "[yellow]Generating waveform data...[/]",
                        title="[bold blink]Audio Waveform[/]",
                        border_style="cyan"
                    ))
                
                # Generate waveform data
                waveform_data = self.waveform_manager.generate_waveform_data(audio_file)
                
                if waveform_data and self.waveform_active:
                    # Get terminal width for optimal display
                    terminal_width = self.live.console.size.width if self.live else 120
                    
                    # Render waveform
                    waveform_display = self.waveform_manager.render_footer_waveform(
                        terminal_width, self.waveform_height
                    )
                    
                    # Get file info
                    file_info = self.waveform_manager.get_file_info()
                    
                    # Update footer with waveform
                    waveform_content = f"{file_info}\n\n{waveform_display}"
                    
                    self.update_layout("footer.waveform", Panel(
                        waveform_content,
                        title="[bold]Audio Waveform[/]",
                        border_style="cyan"
                    ))
                    
            except Exception as e:
                if self.waveform_active:
                    self.update_layout("footer.waveform", Panel(
                        f"[red]Waveform error: {str(e)}[/]",
                        title="[bold]Audio Waveform[/]",
                        border_style="red"
                    ))
        
        # Start generation thread
        self.waveform_update_thread = threading.Thread(target=generate_waveform, daemon=True)
        self.waveform_update_thread.start()
    
    def update_waveform_display(self):
        """Update waveform display with current data"""
        if not self.waveform_active or not self.waveform_manager.waveform_data:
            return
            
        try:
            # Get terminal width for optimal display
            terminal_width = self.live.console.size.width if self.live else 120
            
            # Render waveform
            waveform_display = self.waveform_manager.render_footer_waveform(
                terminal_width, self.waveform_height
            )
            
            # Get file info
            file_info = self.waveform_manager.get_file_info()
            
            # Update footer with waveform
            waveform_content = f"{file_info}\n\n{waveform_display}"
            
            self.update_layout("footer.waveform", Panel(
                waveform_content,
                title="[bold]Audio Waveform[/]",
                border_style="cyan"
            ))
            
        except Exception as e:
            self.update_layout("footer.waveform", Panel(
                f"[red]Waveform display error: {str(e)}[/]",
                title="[bold]Audio Waveform[/]",
                border_style="red"
            ))
    
    def update_input_display(self):
        """Update input display in content area"""
        if self.input_active:
            waveform_status = "[green]ON[/]" if self.waveform_active else "[dim]OFF[/]"
            controls_hint = (
                f"[dim]Press ENTER to download • ESC to quit\n"
                f"Waveform display: {waveform_status} (w/t to toggle, h to hide)[/]"
            )
            
            input_panel = Panel(
                f"[bold cyan]Enter YouTube URL:[/]\n" +
                f"[yellow]> {self.input_buffer}[/]\n\n" +
                controls_hint,
                border_style="cyan",
                title="[bold]Input[/]"
            )
        else:
            input_panel = Panel(
                "[dim]Processing...[/]",
                border_style="yellow"
            )
        self.update_layout("content", input_panel)
        
    def show_spinner(self, message, spinner_type="dots"):
        """Show spinner in content area"""
        spinner = Spinner(spinner_type, text=message)
        content = Panel(
            Columns([
                spinner,
                f"[yellow]{message}[/]"
            ], align="center"),
            border_style="yellow",
            title="[blink]Processing[/blink]"
        )
        self.update_layout("content", content)
        
    def update_sidebar(self, content):
        """Update sidebar with download info"""
        self.update_layout("sidebar", content)
        
    def process_char(self, char):
        """Process individual character input"""
        if not self.input_active:
            return
            
        if ord(char) == 13:  # Enter
            if self.input_buffer.strip():
                self.start_download(self.input_buffer.strip())
                self.input_buffer = ""
        elif ord(char) == 27:  # Escape
            self.running = False
        elif char.lower() == 'w' and not self.input_buffer:
            # Toggle waveform display (only when input is empty)
            self.toggle_waveform_display()
        elif char.lower() == 't' and not self.input_buffer:
            # Toggle waveform display (alternative key, only when input is empty)
            self.toggle_waveform_display()
        elif char.lower() == 'h' and not self.input_buffer:
            # Hide waveform (only when input is empty)
            if self.waveform_active:
                self.toggle_waveform_display()
        elif ord(char) == 127:  # Backspace
            if self.input_buffer:  # Only update if there's something to delete
                self.input_buffer = self.input_buffer[:-1]
                self.update_input_display()
        elif ord(char) >= 32:  # Printable characters
            self.input_buffer += char
            self.update_input_display()
            
    def start_download(self, url):
        """Start download in separate thread"""
        self.input_active = False
        self.current_status = "downloading"
        
        # Start download thread
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(url,),
            daemon=True
        )
        self.download_thread.start()
        
        # Start progress monitoring
        progress_thread = threading.Thread(
            target=self._monitor_progress,
            daemon=True
        )
        progress_thread.start()
        
    def _download_worker(self, url):
        """Worker thread for download and conversion"""
        try:
            self.progress_queue.put(("status", "Getting video info..."))
            
            # Get video info
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                video_title = info_dict.get("title", "Unknown")
                safe_title = sanitize_filename(video_title)
            
            self.progress_queue.put(("info", {"title": video_title, "safe_title": safe_title}))
            self.progress_queue.put(("status", "Starting download..."))
            
            # Download setup
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{safe_title}.%(ext)s",
                "quiet": True,
                "progress_hooks": [self._progress_hook],
            }
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.progress_queue.put(("status", "Converting to MP3..."))
            
            # Convert to MP3
            mp3_file = f"{safe_title}.mp3"
            if Mp3fy(f"{safe_title}.webm", mp3_file):
                try:
                    os.remove(f"{safe_title}.webm")
                    file_size = os.path.getsize(mp3_file) / 1024 / 1024
                    self.progress_queue.put(("complete", {
                        "file": mp3_file,
                        "size": file_size
                    }))
                except Exception as e:
                    self.progress_queue.put(("error", f"Cleanup error: {str(e)}"))
            else:
                self.progress_queue.put(("error", "MP3 conversion failed"))
                
        except Exception as e:
            self.progress_queue.put(("error", str(e)))
            
    def _progress_hook(self, d):
        """Progress hook for yt-dlp"""
        if d["status"] == "downloading":
            if d.get("total_bytes"):
                progress = (d["downloaded_bytes"] / d["total_bytes"]) * 100
                self.progress_queue.put(("progress", progress))
            elif d.get("total_bytes_estimate"):
                progress = (d["downloaded_bytes"] / d["total_bytes_estimate"]) * 100
                self.progress_queue.put(("progress", progress))
        elif d["status"] == "finished":
            self.progress_queue.put(("progress", 100))
            
    def _monitor_progress(self):
        """Monitor progress updates and update UI"""
        video_info = None
        
        while self.current_status == "downloading":
            try:
                msg_type, data = self.progress_queue.get(timeout=0.1)
                
                if msg_type == "status":
                    self.show_spinner(data, "material")
                    
                elif msg_type == "info":
                    video_info = data
                    self.update_sidebar(Panel(
                        f"[bold yellow]{data['title'][:30]}...[/]\n" +
                        f"[cyan]Preparing download...[/]",
                        title="[bold]Video Info[/]",
                        border_style="blue"
                    ))
                    
                elif msg_type == "progress":
                    if video_info:
                        progress_bar = "[" + "█" * int(data/5) + "·" * (20-int(data/5)) + "]"
                        self.update_layout("content", Panel(
                            f"[bold]Downloading: {video_info['title'][:25]}...[/]\n\n" +
                            f"{progress_bar} {data:.1f}%\n\n" +
                            f"[dim]Please wait...[/]",
                            border_style="green",
                            title="[blink]Download Progress[/blink]"
                        ))
                        
                elif msg_type == "complete":
                    self.current_status = "complete"
                    self.current_file = data['file']
                    
                    self.update_completion_display()
                    
                    self.update_sidebar(Panel(
                        f"[green]✓ {data['file']}[/]\n" +
                        f"[yellow]Size:[/] {data['size']:.2f} MB",
                        title="[bold]Latest Download[/]",
                        border_style="green"
                    ))
                    
                    # Automatically generate waveform if display is active
                    if self.waveform_active:
                        self.start_waveform_generation(self.current_file)
                    
                elif msg_type == "error":
                    self.update_layout("content", Panel(
                        f"[bold red]✗ Error occurred![/]\n\n" +
                        f"[yellow]Error:[/] {data}\n\n" +
                        f"[cyan]Press any key to continue[/]",
                        border_style="red",
                        title="[bold]Error[/]"
                    ))
                    self.current_status = "error"
                    
            except queue.Empty:
                continue
    
    def update_completion_display(self):
        """Update completion display with enhanced controls"""
        if not self.current_file:
            return
            
        controls_text = (
            "[cyan]Controls:[/]\n"
            "[bold]w[/] - Toggle waveform in footer\n"
            "[bold]f[/] - Full-screen waveform view\n" 
            "[bold]ENTER[/] - New download\n"
            "[bold]ESC[/] - Quit"
        )
        
        file_size = os.path.getsize(self.current_file) / 1024 / 1024 if os.path.exists(self.current_file) else 0
        
        self.update_layout("content", Panel(
            f"[bold green]✓ Download Complete![/]\n\n" +
            f"[yellow]File:[/] {self.current_file}\n" +
            f"[yellow]Size:[/] {file_size:.2f} MB\n\n" +
            controls_text,
            border_style="green",
            title="[bold]Success[/]"
        ))
                
    def handle_complete_state(self, char):
        """Handle input when download is complete"""
        if char.lower() == 'w':
            # Toggle waveform in footer
            self.toggle_waveform_display()
        elif char.lower() == 'f':
            # Show full-screen waveform
            self.show_spinner("Generating full waveform...", "hearts")
            threading.Thread(
                target=lambda: [
                    sleep(0.5),  # Brief delay for visual feedback
                    visualize_waveform(self.current_file),
                    self.update_completion_display()
                ],
                daemon=True
            ).start()
        elif char.lower() == 't':
            # Toggle waveform (alternative key)
            self.toggle_waveform_display()
        elif char.lower() == 'h':
            # Hide waveform
            if self.waveform_active:
                self.toggle_waveform_display()
        elif ord(char) == 13:  # Enter - new download
            self.reset_to_input()
        elif ord(char) == 27:  # Escape
            self.running = False
            
    def reset_to_input(self):
        """Reset to input state"""
        self.current_status = "idle"
        self.input_active = True
        self.input_buffer = ""
        self.update_input_display()
        
    def capture_input(self):
        """Capture keyboard input without blocking"""
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            while self.running:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    
                    if self.current_status == "idle":
                        self.process_char(char)
                    elif self.current_status in ["complete", "error"]:
                        self.handle_complete_state(char)
                        
        except Exception as e:
            consola.print(f"[red]Input error: {e}[/red]")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            
    def run(self):
        """Main application entry point"""
        Figlich("Qoossiee", "rgb(255,130,255)", "p", "rowancap")
        
        # Start input capture thread
        input_thread = threading.Thread(target=self.capture_input, daemon=True)
        input_thread.start()
        
        # Start live rendering with higher refresh rate for waveform updates
        with Live(
            self.layout, 
            console=consola, 
            refresh_per_second=10,  # Increased for smoother waveform updates
            screen=True
        ) as live:
            self.live = live
            while self.running:
                # Update waveform display if active and data available
                if self.waveform_active and self.waveform_manager.waveform_data:
                    self.update_waveform_display()
                sleep(0.1)


def maino():
    """Main application entry point - now using enhanced TUI"""
    app = QoosieApp()
    app.run()

if __name__ == "__main__":
    maino()
