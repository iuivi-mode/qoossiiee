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
from time import sleep
import yt_dlp
import ffmpeg
import librosa
import pydub
import pyfiglet
import typer
from rich.console import Console
# from rich import print
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TimeRemainingColumn,
    TransferSpeedColumn,
    SpinnerColumn,
)
from rich.text import Text
from yt_dlp.utils import sanitize_filename

# Activar Consola rich
consola= Console()
consola.print("[green italic] xd oh si [/green italic]")

# Boiler opciones de progress bars
progress_columns = [
    "[progress.description]{task.description}",
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.0f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    ".",
    SpinnerColumn("hearts"),

]


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

def YT_Presta(linku):

    # Get video info first for title
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info_dict = ydl.extract_info(linku, download=False)
        video_title = info_dict.get("title", "Unknown")
        safe_title = sanitize_filename(video_title)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{safe_title}.%(ext)s",
        "merge_output_format": "mp3",
        "quiet": True,  # quita los datos de descarga del cmd`
        "progress_hooks": [],
    }

    # barra progreiso
    with Progress(*progress_columns) as progress:
        download_task = progress.add_task(
            f"[cyan]Descargando... {video_title[:20]}...", total=100
        )

        # Progresso
        def progress_hook(d):
            if d["status"] == "downloading":
                if d.get("total_bytes"):
                    progress.update(
                        download_task,
                        completed=(d["downloaded_bytes"] / d["total_bytes"]) * 100,
                    )
                elif d.get("total_bytes_estimate"):
                    progress.update(
                        download_task,
                        completed=(d["downloaded_bytes"] / d["total_bytes_estimate"])
                        * 100,
                    )
                else:
                    progress.update(download_task, advance=0.5)
            elif d["status"] == "finished":
                progress.update(
                    download_task,
                    completed=100,
                    description="[green]preparando mp3zacion xd...[/green]",
                )

        ydl_opts["progress_hooks"].append(progress_hook)

        try:
            # envolver en Panel
            with progress:
                consola.print(
                    Panel.fit(
                        f"[yellow] :[/yellow] [bold]{video_title}[/bold]\n"
                        f"[magenta]URL:[/magenta] {linku}",
                        title="[blink]Qoosie YT -> MP3[/blink]",
                        border_style="yellow",
                    )
                )

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([linku])

                progress.update(download_task, visible=False)
                consola.print(
                    Panel.fit(
                        f"[bold green]✓ Archivo Descargao![/bold green]\n"
                        f"[yellow]Guardado como:[/yellow] {safe_title}.webm",
                        title="[blink] 🎵 ^🤤^🤤^🤤^ 🎵 [/blink]",
                        border_style="green",
                    )
                )
                return safe_title
        except Exception as e:
            consola.print(
                Panel.fit(
                    f"[bold red]✗ la descarga fallo xc![/bold red]\n"
                    f"[yellow]Error:[/yellow] {str(e)}",
                    title="[blink]⚠️ Error ⚠️[/blink]",
                    border_style="red",
                )
            )


def casa():
    layouto = Layout()

    layouto.split_column(
        Layout(name="headero"),
        Layout(name="cuerpo"),
        Layout(name="footah"),
    )

    layouto["cuerpo"].split_row(
        Layout(name="izq"),
        Layout(name="dere"),
    )
    consola.print(layouto)

def maino():
    Figlich("Qoossiee", "rgb(255,130,255)", "p", "rowancap")
    casa()
    while True:
        consola.print(f"\n[bold yellow] YouTube link para descarga 🔽 [/bold yellow]")
        linkon = str(input()).strip()

        if linkon:
            webm_file = YT_Presta(linkon)
            if webm_file:  # si existe el archivo procedemos
                mp3_file = f"{webm_file}.mp3"
                if Mp3fy(f"{webm_file}.webm", mp3_file):
                    # eliminar archivo webm no se ocupa
                    try:
                        os.remove(f"{webm_file}.webm")
                        consola.print(f"[blink]eliminando: {webm_file}.webm ... [/blink]")
                    except Exception as e:
                        consola.print(f"[red]fallo eliminar .webm! =0 : {str(e)}[/red]")

            # Descargar otro archivo?
            consola.print("\n[bold italics cyan] Descargar otro? (y/n): [/bold italics cyan]")
            if input().lower() != "y":
                Figlich("modmo", "bold rgb(30,255,240)", "pf", "bear")
                break


if __name__ == "__main__":
    maino()
