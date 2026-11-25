import argparse
import json
import os
import re
import subprocess
import time
import unicodedata

def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    texto = re.sub(r"[-\s]+", "_", texto)
    return texto or "proyecto_sin_nombre"

def main():
    parser = argparse.ArgumentParser(description="Aplica Zoom Dinámico Programático (Punch-In / Punch-Out) sincronizado con el diálogo")
    parser.add_argument("--proyecto", "-p", default="", help="Nombre del proyecto")
    parser.add_argument("--video", "-v", required=True, help="Ruta al video de entrada (ej: insumos/slug/video_sinPausas.mp4)")
    parser.add_argument("--out", "-o", default="", help="Ruta de salida del video renderizado")
    parser.add_argument("--scale", type=float, default=1.0, help="Escala de render (1.0 = 1080x1920, 0.5 = 540x960)")
    parser.add_argument("--crf", type=int, default=22, help="CRF de compresión (def: 22, o 28 para preview)")
    args = parser.parse_args()

    video_path = os.path.normpath(args.video).replace("\\", "/")
    if not os.path.exists(video_path):
        print(f"Error: Video no encontrado en {video_path}")
        return

    # Extraer proyecto y nombre base
    partes = video_path.split("/")
    nombre_archivo = os.path.basename(video_path)
    nombre_base = os.path.splitext(nombre_archivo)[0]

    if not args.proyecto and len(partes) >= 2 and partes[0] == "insumos":
        proyecto = partes[1]
    else:
        proyecto = args.proyecto or "general"

    carpeta_salida = os.path.join("salida", proyecto)
    os.makedirs(carpeta_salida, exist_ok=True)

    out_video = args.out or os.path.join(carpeta_salida, f"{nombre_base}_zoom.mp4")

    # Asegurar que el video está en remotion/public/<proyecto>/
    public_dir = os.path.join("remotion", "public", proyecto)
    os.makedirs(public_dir, exist_ok=True)
    public_video = os.path.join(public_dir, nombre_archivo)
    if not os.path.exists(public_video):
        import shutil
        shutil.copy2(video_path, public_video)
        print(f"Video copiado a public: {public_video}")

    rel_video_src = f"{proyecto}/{nombre_archivo}"

    print(f"\n=== ZOOM DINÁMICO PROGRAMÁTICO ===")
    print(f"Video entrada : {video_path}")
    print(f"Composición   : Inicio2Zoom")
    print(f"Resolución    : {'1080x1920 (Full HD)' if args.scale == 1.0 else '540x960 (Preview)'}")
    print(f"Destino       : {out_video}")

    ruta_remotion = os.path.abspath("remotion")
    ruta_salida_abs = os.path.abspath(out_video).replace("\\", "/")

    cmd = [
        "npx", "remotion", "render",
        "Inicio2Zoom",
        ruta_salida_abs,
        f"--scale={args.scale}",
        f"--crf={args.crf}",
        "--overwrite"
    ]

    t_start = time.time()
    subprocess.run(cmd, cwd=ruta_remotion, shell=True, check=True)
    t_total = time.time() - t_start

    tam_mb = os.path.getsize(out_video) / (1024 * 1024) if os.path.exists(out_video) else 0
    print(f"\n Video con Zoom Dinámico generado exitosamente:")
    print(f"  ├─ Tiempo de render : {t_total:.1f} segundos")
    print(f"  ├─ Tamaño archivo   : {tam_mb:.2f} MB")
    print(f"  └─ Ubicación        : {out_video}\n")

if __name__ == "__main__":
    main()
