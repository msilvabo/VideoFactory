import os
import subprocess
import numpy as np

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

def main():
    audio_in = "insumos/2026_11_23_falta_de_contexto/medio.mp3"
    video_in = "insumos/2026_11_23_falta_de_contexto/medio_2_limpio_sinPausas.mp4"
    audio_synced = "insumos/2026_11_23_falta_de_contexto/medio_ajustado.wav"
    video_out = "salida/2026_11_23_falta_de_contexto/medio.mp4"
    video_out_root = "salida/medio.mp4"

    os.makedirs("salida/2026_11_23_falta_de_contexto", exist_ok=True)
    os.makedirs("salida", exist_ok=True)

    # Segmentos de medio.mp3 mapeados a targets en el video
    # 1. "Un análisis de Emergence en noviembre del 26"
    #    medio.mp3: 1.38s - 3.96s (dur: 2.58s) -> target video: 0.10s - 3.20s (dur: 3.10s)
    #    ratio: 2.58 / 3.10 = 0.832 (atempo=0.832)
    #
    # 2. "indica que muchos de estos errores que se están dando en producciones"
    #    medio.mp3: 4.18s - 8.38s (dur: 4.20s) -> target video: 3.80s - 6.42s (dur: 2.62s)
    #    ratio: 4.20 / 2.62 = 1.603 (atempo=1.603)
    #
    # 3. "porque los programadores están delegando"
    #    medio.mp3: 8.38s - 10.60s (dur: 2.22s) -> target video: 7.04s - 8.96s (dur: 1.92s)
    #    ratio: 2.22 / 1.92 = 1.156 (atempo=1.156)
    #
    # 4A. "código a la IA"
    #    medio.mp3: 10.60s - 11.52s (dur: 0.92s) -> target video: 8.96s - 9.80s (dur: 0.84s)
    #    ratio: 0.92 / 0.84 = 1.095 (atempo=1.095)
    #
    # 4B. "sin el suficiente contexto."
    #    medio.mp3: 12.20s - 13.68s (dur: 1.48s) -> target video: 9.85s - 11.10s (dur: 1.25s)
    #    ratio: 1.48 / 1.25 = 1.184 (atempo=1.184)

    # Construimos el audio final ensamblado con adelay y amix / concat
    filter_complex = (
        # Seg 1: 1.38 a 3.96 -> atempo=0.832 -> adelay a 100ms
        "[0:a]atrim=start=1.38:end=3.96,asetpts=PTS-STARTPTS,atempo=0.832,adelay=100|100[a1];"
        # Seg 2: 4.18 a 8.38 -> atempo=1.603 -> adelay a 3800ms
        "[0:a]atrim=start=4.18:end=8.38,asetpts=PTS-STARTPTS,atempo=1.603,adelay=3800|3800[a2];"
        # Seg 3: 8.38 a 10.60 -> atempo=1.156 -> adelay a 7040ms
        "[0:a]atrim=start=8.38:end=10.60,asetpts=PTS-STARTPTS,atempo=1.156,adelay=7040|7040[a3];"
        # Seg 4A: 10.60 a 11.52 -> atempo=1.095 -> adelay a 8960ms
        "[0:a]atrim=start=10.60:end=11.52,asetpts=PTS-STARTPTS,atempo=1.095,adelay=8960|8960[a4a];"
        # Seg 4B: 12.20 a 13.68 -> atempo=1.184 -> adelay a 9850ms
        "[0:a]atrim=start=12.20:end=13.68,asetpts=PTS-STARTPTS,atempo=1.184,adelay=9850|9850[a4b];"
        # Mezcla final de todas las pistas sincronizadas
        "[a1][a2][a3][a4a][a4b]amix=inputs=5:duration=longest:dropout_transition=0,volume=2.2[outa]"
    )

    cmd_audio = [
        "ffmpeg", "-y", "-v", "error",
        "-i", audio_in,
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-t", "11.327",
        audio_synced
    ]
    print("Sincronizando audio por tramos...")
    subprocess.run(cmd_audio, check=True)
    print(f"Audio sincronizado generado: {audio_synced}")

    # Ahora remux con el video medio_2_limpio_sinPausas.mp4
    cmd_mux = [
        "ffmpeg", "-y", "-v", "error",
        "-i", video_in,
        "-i", audio_synced,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-t", "11.327",
        video_out
    ]
    print(f"Generando video remux: {video_out}...")
    subprocess.run(cmd_mux, check=True)

    # Copiar también a salida/medio.mp4
    import shutil
    shutil.copy2(video_out, video_out_root)
    print(f"Copiado a: {video_out_root}")
    print("¡Proceso completado exitosamente!")

if __name__ == "__main__":
    main()
