import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import unicodedata

def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    texto = re.sub(r"[-\s]+", "_", texto)
    return texto or "proyecto_sin_nombre"

def resolver_carpetas(proyecto: str):
    slug = slugify(proyecto)
    rutas = {
        "slug": slug,
        "insumos": os.path.join("insumos", slug),
        "salida": os.path.join("salida", slug),
        "public": os.path.join("remotion", "public", slug),
    }
    for clave in ("insumos", "salida", "public"):
        os.makedirs(rutas[clave], exist_ok=True)
    return rutas

def buscar_audio_estudio_externo(carpeta_insumos: str):
    """
    Busca si el usuario colocó un audio mejorado con Adobe Podcast o ElevenLabs
    (ej: audio_mejorado.wav, toma1_enhanced.wav, etc.)
    """
    patrones = ("*_mejorado.*", "*_enhanced.*", "*_limpio.*", "audio_estudio.*", "audio_clean.*")
    for pat in patrones:
        encontrados = glob.glob(os.path.join(carpeta_insumos, pat))
        if encontrados:
            return encontrados[0]
    return None

def extraer_audio_crudo(video_path: str, out_wav: str):
    """
    Extrae la pista de audio sin comprimir (PCM 16-bit 48kHz Stereo/Mono) usando FFmpeg.
    """
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "48000",
        out_wav
    ]
    subprocess.run(cmd, check=True)

def aplicar_filtro_viento_y_presencia(in_audio: str, out_audio: str, corte_viento_hz=115, formato="mp3"):
    """
    Aplica una cadena acústica para suprimir viento de terraza y mejorar la presencia vocal:
    1. highpass: corta el retumbo sordo por debajo de corte_viento_hz (ej. 115Hz).
    2. afftdn: reduce el soplido y ruido de fondo continuo.
    3. equalizer: leve realce de presencia y claridad vocal en 3.2 kHz (+3dB).
    4. compand: compresión dinámica para nivelar picos y ráfagas.
    5. loudnorm: normalización para redes sociales a -16 LUFS.
    """
    filtro = (
        f"highpass=f={corte_viento_hz},"
        f"afftdn=nf=-24:tn=1,"
        f"equalizer=f=3200:width_type=h:width=600:g=3,"
        f"compand=attacks=0.02:decays=0.15:points=-80/-80|-40/-30|-20/-15|0/-6:gain=2,"
        f"loudnorm=I=-16:TP=-1.5:LRA=11"
    )

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", in_audio,
        "-af", filtro,
    ]

    if formato.lower() == "mp3":
        cmd.extend(["-c:a", "libmp3lame", "-b:a", "320k", out_audio])
    else:
        cmd.extend(["-acodec", "pcm_s16le", "-ar", "48000", out_audio])

    subprocess.run(cmd, check=True)

def procesar_video(video_path: str, rutas: dict, corte_viento_hz: int, formato="mp3"):
    nombre_base = os.path.splitext(os.path.basename(video_path))[0]
    ext_audio = f".{formato.lower()}"
    
    # 1. Rutas de salida en insumos/<slug>/
    temp_wav_crudo = os.path.join(rutas["insumos"], f"temp_{nombre_base}_crudo.wav")
    audio_final_insumos = os.path.join(rutas["insumos"], f"{nombre_base}{ext_audio}")
    
    # 2. Rutas espejo en remotion/public/<slug>/
    audio_public = os.path.join(rutas["public"], f"{nombre_base}{ext_audio}")

    print(f"\n Procesando video: {os.path.basename(video_path)}")
    print(f"  ├─ Extrayendo audio base a 48kHz...")
    extraer_audio_crudo(video_path, temp_wav_crudo)

    print(f"  ├─ Aplicando mejoras (Corte viento {corte_viento_hz}Hz + Denoise + Loudnorm -> {formato.upper()} 320k)...")
    aplicar_filtro_viento_y_presencia(temp_wav_crudo, audio_final_insumos, corte_viento_hz=corte_viento_hz, formato=formato)

    # Eliminar temporal
    if os.path.exists(temp_wav_crudo):
        os.remove(temp_wav_crudo)

    # Copiar a public para Remotion
    shutil.copy2(audio_final_insumos, audio_public)
    print(f"  ├─ Insumos : {audio_final_insumos}")
    print(f"  └─ Remotion: {audio_public}")

    return audio_final_insumos

def main():
    parser = argparse.ArgumentParser(description="Extractor y limpiador de audio contra viento de teléfono para VideoFactory")
    parser.add_argument("--proyecto", "-p", required=True, help="Nombre del proyecto o versión (ej. 'video lunes parte 1')")
    parser.add_argument("--video", "-v", default="", help="Ruta o nombre de video específico. Si se omite, procesa todos los videos del proyecto")
    parser.add_argument("--corte_viento", type=int, default=115, help="Frecuencia en Hz para cortar retumbo de viento (def: 115)")
    parser.add_argument("--formato", "-f", default="mp3", choices=["mp3", "wav"], help="Formato de audio de salida (def: mp3)")
    args = parser.parse_args()

    rutas = resolver_carpetas(args.proyecto)
    print(f"\n=== EXTRACTOR Y OPTIMIZADOR DE AUDIO ===")
    print(f"Proyecto : {rutas['slug']}")
    print(f"Carpeta  : {rutas['insumos']}")
    print(f"Formato  : {args.formato.upper()} (Alta calidad)")

    # 1. Comprobar si ya existe un audio de estudio externo subido por el usuario
    audio_estudio = buscar_audio_estudio_externo(rutas["insumos"])
    if audio_estudio:
        print(f"\n ⭐ DETECTADO AUDIO DE ESTUDIO EXTERNO (Adobe Podcast / ElevenLabs):")
        print(f"    Archivo: {audio_estudio}")
        ext_estudio = os.path.splitext(audio_estudio)[1]
        destino_public = os.path.join(rutas["public"], f"audio_final{ext_estudio}")
        shutil.copy2(audio_estudio, destino_public)
        print(f"    Se prioriza automáticamente y se enlaza a Remotion en: {destino_public}\n")
        return

    # 2. Buscar videos a procesar
    videos_a_procesar = []
    if args.video:
        # Puede ser ruta absoluta/relativa o solo el nombre dentro de insumos/<slug>/
        if os.path.exists(args.video):
            videos_a_procesar.append(args.video)
        else:
            candidato = os.path.join(rutas["insumos"], args.video)
            if os.path.exists(candidato):
                videos_a_procesar.append(candidato)
            else:
                print(f"Error: No se encontró el video '{args.video}' en {rutas['insumos']}")
                sys.exit(1)
    else:
        # Modo por lotes: buscar todos los videos en insumos/<slug>/
        for ext in ("*.mp4", "*.mov", "*.mkv", "*.webm"):
            videos_a_procesar.extend(glob.glob(os.path.join(rutas["insumos"], ext)))

    if not videos_a_procesar:
        print(f"\nNo se encontraron videos (.mp4, .mov, etc.) en {rutas['insumos']}/.")
        print(f"Coloca tus grabaciones de teléfono allí y vuelve a ejecutar el comando.")
        return

    print(f"Se procesarán {len(videos_a_procesar)} video(s)...")

    ultimo_audio = None
    for vid in sorted(videos_a_procesar):
        ultimo_audio = procesar_video(vid, rutas, args.corte_viento, formato=args.formato)

    # Si hay un único video o el último procesado, enlazarlo también como 'audio_final.<ext>' en public
    if ultimo_audio:
        ext_final = f".{args.formato.lower()}"
        destino_general = os.path.join(rutas["public"], f"audio_final{ext_final}")
        shutil.copy2(ultimo_audio, destino_general)

    print(f"\n Extracción y filtrado completado exitosamente.")

if __name__ == "__main__":
    main()
