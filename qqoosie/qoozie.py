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
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import time
from datetime import datetime
import sys
import numpy as np
import threading
import queue

from sola import(csola,mMxVv,bathroo,footha_instructor,TextTagga,RandoGB,random)

from audio_jUnkQoo import Yt_mp3fryer

# Create layout
casaA = Layout()

casaA.split_column(
    Layout(size=5,name="headz"),
    Layout(name="cuerpo"),
    Layout(size=3, name="footr")
)

casaA["cuerpo"].split_row(
    Layout(ratio=2,name="hotzspot"),
    Layout(name="logstats"),
)

casaA["logstats"].split_column(
    Layout(name="misc"),
    Layout(ratio=2,name="statss"),
)

# Create thread-safe queue for progress updates
progress_queue = queue.Queue()

# Custom progress display for downloads
class DownloadProgress:
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn("bouncingBall"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            SpinnerColumn("pong"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            SpinnerColumn("earth"),
            SpinnerColumn("runner"),

        )
        self.tasks = {}  # Track multiple tasks by phase name
        self.message = ""

    def add_phase(self, phase_name, description, total=100):
        """Add a new progress phase"""
        if phase_name not in self.tasks:
            task_id = self.progress.add_task(description, total=total)
            self.tasks[phase_name] = task_id
        return self.tasks[phase_name]

    def update_phase(self, phase_name, percent, description=None):
        """Update a specific phase"""
        if phase_name in self.tasks:
            task_id = self.tasks[phase_name]
            if description:
                self.progress.update(task_id, completed=percent, description=f"[cyan]{description}")
            else:
                self.progress.update(task_id, completed=percent)

    def update(self, percent, status, message=""):
        """Legacy update method for backward compatibility"""
        if not self.tasks:
            # Create default task if none exist
            self.add_phase("default", f"[cyan]{status}")

        # Update the first/default task
        first_phase = list(self.tasks.keys())[0]
        self.update_phase(first_phase, percent, status)
        self.message = message

    def __rich__(self):
        return self.progress

    def get_panel(self, style):
        return Panel(
            self.progress,
            title="u2m",
            style=style,
            subtitle=self.message
        )

try:
    chicle = f"rgb({RandoGB(1,255,'s')[0]},{RandoGB(1,255,'s')[1]},{RandoGB(1,255,'s')[2]})"
    bathcolor = f"rgb({RandoGB(25,255,'s')[0]},{RandoGB(1,255,'s')[1]},{RandoGB(25,255,'s')[2]})"

    # Get URL before Live display
    csola.print(f"[{bathcolor}]Inserte Youtube URL: [/{bathcolor}]", end="")
    zelda = input().strip()

    # Create progress tracker
    download_progress = DownloadProgress()

    # Create panel for download progress
    progress_panel = download_progress.get_panel(chicle)

    # Thread function for downloading
    def download_thread():
        try:
            # Update progress - starting
            progress_queue.put(("update", 0, "D 3 S Kr G A N D 0 . . .", ""))

            # Run download and conversion
            result = Yt_mp3fryer(zelda, progress_queue)

            # Update progress - finished
            progress_queue.put(("update", 100, "Descargao e Convertio'!", result))
        except Exception as e:
            progress_queue.put(("error", 0, "Algo Vlv no hay descarga :( ", str(e)))

    # Start download thread
    threading.Thread(target=download_thread, daemon=True).start()

    with Live(casaA, refresh_per_second=10, screen=True) as live:
        footr_indx = 0
        headrPanel_index = 0

        headero = Panel(
            TextTagga("QoOzZi",'C'),
            highlight=True,
            expand=True,
            box=box.HEAVY_EDGE,
            style=f"bold {chicle} "
        )

        headero2 = Panel(
            TextTagga("Mp3fya","C"),
            highlight=True,
            expand=True,
            box=box.HEAVY_EDGE,
            style=f"bold {chicle} "
        )
        headers = [headero, headero2]

        # Footer panel
        tui_room = Panel(
            f"[{bathcolor}]{bathroo}[/{bathcolor}]",
            title="bathmap",
            style=f"{chicle}"
        )
        casaA["misc"].update(tui_room)

        # Initial progress display
        casaA["hotzspot"].update(progress_panel)

        # Animation loop
        while True:
            # Process progress updates
            while not progress_queue.empty():
                update_type, *data = progress_queue.get()
                if update_type == "add_phase":
                    phase_name, description, total = data
                    download_progress.add_phase(phase_name, description, total)
                    progress_panel = download_progress.get_panel(chicle)
                elif update_type == "update_phase":
                    phase_name, percent, description = data
                    download_progress.update_phase(phase_name, percent, description)
                    progress_panel = download_progress.get_panel(chicle)
                elif update_type == "update":
                    percent, status, message = data
                    download_progress.update(percent, status, message)
                    progress_panel = download_progress.get_panel(chicle)
                elif update_type == "error":
                    _, status, message = data
                    progress_panel = Panel(
                        f"[red]ERROR: {status}\n{message}[/red]",
                        title="u2m",
                        style=chicle
                    )
# Update all UI elements
            casaA["hotzspot"].update(progress_panel)
            casaA["headz"].update(headers[headrPanel_index])

            footha_info = Panel(
                f"[{bathcolor}]{random.choice(footha_instructor)}[/{bathcolor}]",
                subtitle=mMxVv,
                subtitle_align="right",
                style=f"{chicle} "

            )
            casaA["footr"].update(footha_info)
            headrPanel_index = (headrPanel_index + 1) % len(headers)
            time.sleep(0.2)  # Faster refresh for smoother animation

except KeyboardInterrupt:
    csola.print("\n[bold yellow]Lejos de donde estabamos...[/bold yellow]")
