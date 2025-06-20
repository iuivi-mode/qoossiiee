
import numpy as np
import matplotlib.pylab as plteo
import seaborn as sns

from glob import glob

import librosa
import librosa.display
# audio_jUnkQoo.py
import os
import yt_dlp
from yt_dlp.utils import sanitize_filename
import ffmpeg
import time

def Yout_be_Comper(zelda, progress_queue):
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info_vid = ydl.extract_info(zelda, download=False)
            vid_titulo = info_vid.get("title", "Unknown")
            titulo_limpio = sanitize_filename(vid_titulo)

        ydl_xd = {
            "format": "bestaudio/best",
            "outtmpl": f"{titulo_limpio}.%(ext)s",
            "merge_output_format": "mp3",
            "quiet": True,
            "progress_hooks": [lambda d: progress_hook(d, progress_queue)],
        }

        with yt_dlp.YoutubeDL(ydl_xd) as ydl:
            ydl.download([zelda])
            progress_queue.put(("update_phase", "download", 100, "☻u☻Descarga Completa🪼⋆｡𖦹°🫧⋆.ೃ࿔*:･"))

        return titulo_limpio
    except Exception as e:
        progress_queue.put(("error", 0, "Download failed", str(e)))
        return None

def progress_hook(d, progress_queue):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip('%')
        try:
            percent_float = float(percent)
            progress_queue.put(("update_phase", "download", percent_float, "7u7Descargando7u7"))
        except ValueError:
            pass

def Mp3fy(input_file, output_file, progress_queue):
    try:
        if not os.path.exists(input_file):
            progress_queue.put(("error", 0, "File not found", input_file))
            return False

        progress_queue.put(("update_phase", "convert", 0, "Mp3fying"))

        # Simulate conversion progress
        for i in range(1, 101):
            time.sleep(0.05)  # Simulate conversion time
            progress_queue.put(("update_phase", "convert", i, "Mp3fying"))

        # Actual conversion would happen here
        # (ffmpeg code would go here, progress simulation removed for production)
        # creas archivo a crear con suus  requerimientos
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

        return True
    except Exception as e:
        progress_queue.put(("error", 0, "Fallo Conversion", str(e)))
        return False

def Yt_mp3fryer(linkon, progress_queue):
    if linkon:
        # Add preparation phase
        progress_queue.put(("add_phase", "prepare", "ʕ̢̣̣̣̣̩̩̩̩·͡˔·ོɁ̡̣̣̣̣̩̩̩̩✧Preparando URLεつ▄█▀█●", 100))
        progress_queue.put(("update_phase", "prepare", 0, "ʕ̢̣̣̣̣̩̩̩̩·͡˔·ོɁ̡̣̣̣̣̩̩̩̩✧Preparando URLεつ▄█▀█●"))
        
        # Add download phase
        progress_queue.put(("add_phase", "download", "[white on green] 𐙚⋆°🦢.⋆ᥫ᭡[/white on green]𝄞𝄞𝄞[white]Descargando[/white]...𝄞𝄞𝄞", 100))
        
        # Complete preparation
        progress_queue.put(("update_phase", "prepare", 100, "ʕ̢̣̣̣̣̩̩̩̩·͡˔·ོɁ̡̣̣̣̣̩̩̩̩✧Preparando URLεつ▄█▀█●"))
        
        descargao = Yout_be_Comper(linkon, progress_queue)

        if descargao:
            # Add conversion phase
            progress_queue.put(("add_phase", "convert", "Mp3fying", 100))
            
            dwnMp3 = f"{descargao}.mp3"
            if Mp3fy(f"{descargao}.webm", dwnMp3, progress_queue):
                try:
                    os.remove(f"{descargao}.webm")
                    return f"✩♬ ₊˚.🎧⋆☾⋆⁺₊✧ Guardado como: {dwnMp3}"
                except Exception as e:
                    return f"listo pero no se elimino el .webm: {str(e)}"
            return "Conversion fallo"
        return "Descarga nel"
    return "𒅒𒈔no𒅒diste𒇫𒄆URL 𝐀"
