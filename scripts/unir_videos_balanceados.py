import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata

def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    texto = re.sub(r"[-\s]+", "_", texto)
    return texto or "proyecto_sin_nombre"

def obtener_duracion(archivo: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", archivo
    ]
    try:
        salida = subprocess.check_output(cmd, text=True).strip()
        return float(salida)
    except Exception as e:
        print(f"Error obteniendo duración de {archivo}: {e}")
        return 0.0

def obtener_duraciones_streams(archivo: str):
    """Retorna (duracion_formato, duracion_video, duracion_audio)"""
    cmd = [
        "ffprobe", "-v", "error", "-show_streams", "-show_entries", "format=duration",
        "-of", "json", archivo
    ]
    try:
        salida = subprocess.check_output(cmd, text=True)
        data = json.loads(salida)
        fmt_dur = float(data.get("format", {}).get("duration", 0) or 0)
        v_dur = fmt_dur
        a_dur = fmt_dur
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                v_dur = float(s.get("duration", fmt_dur) or fmt_dur)
            elif s.get("codec_type") == "audio":
                a_dur = float(s.get("duration", fmt_dur) or fmt_dur)
        return fmt_dur, v_dur, a_dur
    except Exception as e:
        dur = obtener_duracion(archivo)
        return dur, dur, dur

def medir_lufs(audio_or_video: str) -> dict:
    cmd = [
        "ffmpeg", "-i", audio_or_video,
        "-af", "ebur128=framelog=verbose",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # Buscar Integrated loudness
    m_i = re.findall(r"I:\s+([-\d.]+)\s+LUFS", res.stderr)
    m_tp = re.findall(r"Peak:\s+([-\d.]+)\s+dBFS", res.stderr)
    m_lra = re.findall(r"LRA:\s+([-\d.]+)\s+LU", res.stderr)
    return {
        "I": float(m_i[-1]) if m_i else -99.0,
        "TP": float(m_tp[-1]) if m_tp else -99.0,
        "LRA": float(m_lra[-1]) if m_lra else 0.0,
    }

def normalizar_clip(video_in: str, video_out: str, target_lufs=-16.0, true_peak=-1.5, lra=9.0):
    """
    Estandariza un clip individual:
    1. Video: 1080x1920 vertical, 30fps, SAR 1:1, centrado sobre fondo oscuro #0B0F19.
       Si el video es más corto que el audio, congela el último cuadro (tpad) para cubrir el audio.
    2. Audio: Compresión dinámica suave + Normalización acústica EBU R128 (loudnorm a target_lufs).
       Si el audio es más corto que el video, lo extiende con silencio (apad).
    """
    fmt_dur, v_dur, a_dur = obtener_duraciones_streams(video_in)
    max_dur = max(fmt_dur, v_dur, a_dur)

    filtro_pad_video = ""
    if v_dur < max_dur - 0.05:
        diff_v = max_dur - v_dur + 0.1
        filtro_pad_video = f",tpad=stop_mode=clone:stop_duration={diff_v:.3f}"

    filtro_v = (
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x0B0F19,"
        f"setsar=1,fps=30{filtro_pad_video}"
    )

    filtro_pad_audio = ""
    if a_dur < max_dur - 0.05:
        filtro_pad_audio = ",apad"

    filtro_a = (
        "aformat=sample_rates=48000:channel_layouts=stereo,"
        "compand=attacks=0.03:decays=0.2:points=-80/-80|-40/-32|-20/-16|0/-8:gain=1.5,"
        f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}{filtro_pad_audio}"
    )

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", video_in,
        "-filter_complex", f"[0:v]{filtro_v}[v];[0:a]{filtro_a}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-t", f"{max_dur:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k",
        video_out
    ]
    subprocess.run(cmd, check=True)

def unir_dos_clips_con_transicion(clip_a: str, clip_b: str, out_path: str, transicion="rebote", trans_dur=0.25):
    """
    Une dos clips normalizados aplicando la transición visual elegida y un micro-crossfade de audio.
    """
    _, dur_a_v, dur_a_a = obtener_duraciones_streams(clip_a)
    dur_a = min(dur_a_v, dur_a_a)
    offset = max(0.0, dur_a - trans_dur)

    # Mapeo de transiciones a filtros xfade de FFmpeg
    xfade_map = {
        "rebote": "zoomin",            # Micro-rebote / zoom elástico
        "zoom_suave": "zoomin",        # Zoom-in rápido continuo
        "fade": "fade",                # Disolvencia cruzada limpia
        "deslizamiento": "smoothleft", # Deslizamiento horizontal suave
        "hblur": "hblur",              # Desenfoque de movimiento horizontal
        "dip_black": "fadeblack",      # Micro-dip suave a negro
    }

    filtro_xfade = xfade_map.get(transicion, "zoomin")

    if transicion == "corte":
        # Concatenación directa sin overlap
        lista_txt = out_path + ".txt"
        with open(lista_txt, "w", encoding="utf-8") as f:
            f.write(f"file '{os.path.abspath(clip_a).replace('\\', '/')}'\n")
            f.write(f"file '{os.path.abspath(clip_b).replace('\\', '/')}'\n")
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-f", "concat", "-safe", "0", "-i", lista_txt,
            "-c", "copy",
            out_path
        ]
        subprocess.run(cmd, check=True)
        if os.path.exists(lista_txt):
            os.remove(lista_txt)
        return

    # Ensamblado con xfade de video + acrossfade de audio
    filter_complex = (
        f"[0:v][1:v]xfade=transition={filtro_xfade}:duration={trans_dur}:offset={offset:.3f}[vout];"
        f"[0:a][1:a]acrossfade=d={trans_dur}:c1=tri:c2=tri[aout]"
    )

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", clip_a,
        "-i", clip_b,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k",
        out_path
    ]
    subprocess.run(cmd, check=True)

def mezclar_musica_fondo(video_in: str, musica_in: str, video_out: str, volumen=0.12):
    filtro = (
        f"[1:a]volume={volumen}[bg];"
        f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", video_in,
        "-stream_loop", "-1", "-i", musica_in,
        "-filter_complex", filtro,
        "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest",
        video_out
    ]
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Une múltiples videos en un orden específico con normalización de voz (EBU R128) y transiciones sutiles")
    parser.add_argument("--proyecto", "-p", default="", help="Nombre del proyecto")
    parser.add_argument("--videos", "-v", nargs="+", default=[], help="Lista de videos en el orden a unir (ej: 1.mp4 2.mp4 3_1.mp4 4.mp4)")
    parser.add_argument("--orden", "-f", default="", help="Archivo de texto con la lista de videos ordenados (opcional)")
    parser.add_argument("--transicion", "-t", default="rebote", choices=["rebote", "zoom_suave", "fade", "deslizamiento", "hblur", "dip_black", "corte"], help="Efecto de transición visual (def: rebote)")
    parser.add_argument("--duracion_transicion", type=float, default=0.25, help="Duración de la transición en segundos (def: 0.25)")
    parser.add_argument("--lufs", type=float, default=-16.0, help="Nivel acústico integrado objetivo (def: -16.0 LUFS)")
    parser.add_argument("--musica", "-m", default="", help="Archivo de música de fondo opcional")
    parser.add_argument("--volumen_musica", type=float, default=0.12, help="Volumen de la música atenuada (def: 0.12)")
    parser.add_argument("--out", "-o", default="", help="Ruta del video final de salida")
    args = parser.parse_args()

    # Determinar proyecto
    proyecto = args.proyecto
    if not proyecto:
        if args.videos and ("salida" in args.videos[0] or "insumos" in args.videos[0]):
            partes = args.videos[0].replace("\\", "/").split("/")
            if len(partes) >= 2:
                proyecto = partes[1]
    proyecto = slugify(proyecto) if proyecto else "general"

    carpeta_salida = os.path.join("salida", proyecto)
    carpeta_insumos = os.path.join("insumos", proyecto)
    os.makedirs(carpeta_salida, exist_ok=True)

    # 1. Determinar lista de videos en orden
    lista_videos = []
    if args.videos:
        lista_videos = args.videos
    elif args.orden and os.path.exists(args.orden):
        with open(args.orden, "r", encoding="utf-8") as f:
            lista_videos = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        # Auto-búsqueda en salida/<proyecto>/ de videos numerados (1.mp4, 2.mp4, 3.mp4 o 3_1.mp4, etc.)
        patrones = ["1*.mp4", "2*.mp4", "3*.mp4", "4*.mp4", "5*.mp4"]
        for pat in patrones:
            encontrados = glob.glob(os.path.join(carpeta_salida, pat))
            if encontrados:
                lista_videos.append(encontrados[0])

    if not lista_videos or len(lista_videos) < 2:
        print(f"Error: Se requieren al menos 2 videos para unir. Videos recibidos: {lista_videos}")
        sys.exit(1)

    # Resolver rutas reales
    rutas_videos = []
    for v in lista_videos:
        if os.path.exists(v):
            rutas_videos.append(os.path.abspath(v))
        elif os.path.exists(os.path.join(carpeta_salida, v)):
            rutas_videos.append(os.path.abspath(os.path.join(carpeta_salida, v)))
        elif os.path.exists(os.path.join(carpeta_insumos, v)):
            rutas_videos.append(os.path.abspath(os.path.join(carpeta_insumos, v)))
        else:
            print(f"Error: Video no encontrado: {v}")
            sys.exit(1)

    out_final = args.out or os.path.join(carpeta_salida, f"{proyecto}_unido.mp4")

    print(f"\n=======================================================")
    print(f" UNIÓN INTELIGENTE DE VIDEOS + NORMALIZACIÓN DE VOZ")
    print(f"=======================================================")
    print(f"Proyecto         : {proyecto}")
    print(f"Cantidad videos  : {len(rutas_videos)}")
    print(f"Transición       : {args.transicion.upper()} ({args.duracion_transicion}s)")
    print(f"Nivel de Voz     : {args.lufs} LUFS (Estándar EBU R128 para Redes)")
    print(f"Salida           : {out_final}")
    print(f"\nOrden de videos:")
    for idx, rv in enumerate(rutas_videos, 1):
        dur = obtener_duracion(rv)
        print(f"  [{idx}] {os.path.basename(rv)} ({dur:.2f}s)")

    temp_dir = tempfile.mkdtemp(prefix="vf_unir_")
    t_start = time.time()

    try:
        # FASE 1: Normalización acústica y visual por clip
        print(f"\n[Fase 1/3] Normalizando audio a {args.lufs} LUFS y resolviendo a 1080x1920@30fps...")
        clips_normalizados = []
        for idx, rv in enumerate(rutas_videos, 1):
            clip_norm = os.path.join(temp_dir, f"norm_clip_{idx:02d}.mp4")
            print(f"  ├─ Procesando [{idx}/{len(rutas_videos)}]: {os.path.basename(rv)}...")
            normalizar_clip(rv, clip_norm, target_lufs=args.lufs)
            clips_normalizados.append(clip_norm)

        # FASE 2: Concatenación secuencial con transiciones sutiles y micro-crossfades
        print(f"\n[Fase 2/3] Ensamblando clips con transición '{args.transicion}'...")
        clip_acumulado = clips_normalizados[0]

        for i in range(1, len(clips_normalizados)):
            clip_siguiente = clips_normalizados[i]
            temp_step = os.path.join(temp_dir, f"step_{i:02d}.mp4")
            print(f"  ├─ Enlazando clip [{i}] con clip [{i+1}] (efecto {args.transicion})...")
            unir_dos_clips_con_transicion(
                clip_acumulado, clip_siguiente, temp_step,
                transicion=args.transicion,
                trans_dur=args.duracion_transicion
            )
            clip_acumulado = temp_step

        # FASE 3: Música de fondo opcional y exportación final
        print(f"\n[Fase 3/3] Finalizando exportación...")
        musica = args.musica
        if not musica:
            musica_def = os.path.join(carpeta_insumos, "musica_fondo.mp3")
            if os.path.exists(musica_def):
                musica = musica_def

        if musica and os.path.exists(musica):
            print(f"  ├─ Mezclando música de fondo: {os.path.basename(musica)} (volumen={args.volumen_musica})...")
            mezclar_musica_fondo(clip_acumulado, musica, out_final, volumen=args.volumen_musica)
        else:
            shutil.copy2(clip_acumulado, out_final)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    t_total = time.time() - t_start
    tam_mb = os.path.getsize(out_final) / (1024 * 1024) if os.path.exists(out_final) else 0
    dur_final = obtener_duracion(out_final)
    lufs_final = medir_lufs(out_final)

    print(f"\n Video final unificado con éxito:")
    print(f"  ├─ Duración total   : {dur_final:.2f} segundos")
    print(f"  ├─ Nivel de Voz     : {lufs_final['I']:.1f} LUFS (Objetivo: {args.lufs} LUFS)")
    print(f"  ├─ True Peak        : {lufs_final['TP']:.1f} dBFS")
    print(f"  ├─ Tamaño archivo   : {tam_mb:.2f} MB")
    print(f"  ├─ Tiempo de render : {t_total:.1f} segundos")
    print(f"  └─ Ubicación        : {out_final}\n")

if __name__ == "__main__":
    main()
