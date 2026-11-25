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

def remux_audio_en_video(video_in: str, audio_in: str, video_out: str):
    """
    Sustituye el audio de un video por un audio mejorado usando Stream Copy para el video
    (-c:v copy), lo que garantiza cero pérdida de calidad visual y ejecución ultra rápida.
    El audio se codifica en AAC a 320 kbps para máxima fidelidad.
    """
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", video_in,
        "-i", audio_in,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "320k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        video_out
    ]
    subprocess.run(cmd, check=True)

def buscar_audio_correspondiente(video_path: str, carpeta_insumos: str):
    """
    Busca el audio mejorado que corresponda a un video (probando .mp3, .wav, etc.)
    """
    nombre_base = os.path.splitext(os.path.basename(video_path))[0]
    
    # 1. Mismo nombre exacto con extension de audio
    for ext in (".mp3", ".wav", ".m4a"):
        candidato = os.path.join(carpeta_insumos, f"{nombre_base}{ext}")
        if os.path.exists(candidato):
            return candidato

    # 2. Con sufijo _limpio o _mejorado
    for ext in (".mp3", ".wav"):
        for sufijo in ("_limpio", "_mejorado", "_audio"):
            candidato = os.path.join(carpeta_insumos, f"{nombre_base}{sufijo}{ext}")
            if os.path.exists(candidato):
                return candidato

    return None

def main():
    parser = argparse.ArgumentParser(description="Reemplaza el audio de un video por audio mejorado con calidad intacta (Lossless Video)")
    parser.add_argument("--proyecto", "-p", required=True, help="Nombre o slug del proyecto")
    parser.add_argument("--video", "-v", default="", help="Video específico a procesar (opcional)")
    parser.add_argument("--audio", "-a", default="", help="Audio específico a inyectar (opcional)")
    parser.add_argument("--sufijo", default="_limpio", help="Sufijo para el video generado (def: _limpio)")
    args = parser.parse_args()

    rutas = resolver_carpetas(args.proyecto)
    print(f"\n=== REEMPLAZO DE AUDIO EN VIDEO (LOSSLESS REMUX) ===")
    print(f"Proyecto : {rutas['slug']}")
    print(f"Carpeta  : {rutas['insumos']}")

    parejas = []

    if args.video:
        # Modo individual
        ruta_vid = args.video if os.path.exists(args.video) else os.path.join(rutas["insumos"], args.video)
        if not os.path.exists(ruta_vid):
            print(f"Error: No existe el video: {args.video}")
            sys.exit(1)

        if args.audio:
            ruta_aud = args.audio if os.path.exists(args.audio) else os.path.join(rutas["insumos"], args.audio)
            if not os.path.exists(ruta_aud):
                print(f"Error: No existe el audio: {args.audio}")
                sys.exit(1)
        else:
            ruta_aud = buscar_audio_correspondiente(ruta_vid, rutas["insumos"])
            if not ruta_aud:
                print(f"Error: No se encontró audio correspondiente para: {os.path.basename(ruta_vid)}")
                sys.exit(1)

        parejas.append((ruta_vid, ruta_aud))
    else:
        # Modo por lote para todo el proyecto
        todos_videos = []
        for ext in ("*.mp4", "*.mov", "*.mkv", "*.webm"):
            todos_videos.extend(glob.glob(os.path.join(rutas["insumos"], ext)))

        # Filtrar videos que ya sean el resultado (_limpio)
        videos_fuente = [v for v in todos_videos if not os.path.splitext(os.path.basename(v))[0].endswith(args.sufijo)]

        for vid in sorted(videos_fuente):
            aud = buscar_audio_correspondiente(vid, rutas["insumos"])
            if aud:
                parejas.append((vid, aud))
            else:
                print(f"  [AVISO] No se encontró audio (.mp3/.wav) para: {os.path.basename(vid)}")

    if not parejas:
        print(f"\nNo se encontraron parejas de video y audio para procesar en {rutas['insumos']}/.")
        return

    print(f"\nSe procesarán {len(parejas)} archivo(s) con reemplazo de audio...\n")

    procesados = 0
    for vid, aud in parejas:
        nombre_base, ext_vid = os.path.splitext(os.path.basename(vid))
        nombre_salida = f"{nombre_base}{args.sufijo}{ext_vid}"
        
        salida_insumos = os.path.join(rutas["insumos"], nombre_salida)
        salida_public = os.path.join(rutas["public"], nombre_salida)

        print(f"🎬 Video: {os.path.basename(vid)}")
        print(f"  ├─ Audio mejorado : {os.path.basename(aud)}")
        print(f"  ├─ Inyectando audio (Stream copy video + AAC 320k)...")
        remux_audio_en_video(vid, aud, salida_insumos)

        # Copiar a public para Remotion
        shutil.copy2(salida_insumos, salida_public)
        print(f"  ├─ Generado en    : {salida_insumos}")
        print(f"  └─ Copiado a Remotion public: {salida_public}\n")
        procesados += 1

    print(f" {procesados} video(s) con audio mejorado generados con éxito sin pérdida de calidad visual.\n")

if __name__ == "__main__":
    main()
