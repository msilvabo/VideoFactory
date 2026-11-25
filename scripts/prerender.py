import argparse
import os
import re
import subprocess
import sys
import time
import unicodedata

def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    texto = re.sub(r"[-\s]+", "_", texto)
    return texto or "proyecto_sin_nombre"

def main():
    parser = argparse.ArgumentParser(description="Prerenderizado rápido en baja calidad para vista previa inmediata en Remotion")
    parser.add_argument("--proyecto", "-p", default="", help="Nombre del proyecto (opcional)")
    parser.add_argument("--composicion", "-c", default="ShortRedesDemo", help="Composición a renderizar (def: ShortRedesDemo)")
    parser.add_argument("--out", "-o", default="", help="Ruta del video preview de salida")
    parser.add_argument("--scale", type=float, default=0.5, help="Escala de resolución (def: 0.5 = 540x960)")
    parser.add_argument("--crf", type=int, default=28, help="Calidad CRF de compresión rápida (def: 28)")
    parser.add_argument("--props", default="", help="Propiedades JSON adicionales para Remotion")
    args = parser.parse_args()

    slug = slugify(args.proyecto) if args.proyecto else ""
    carpeta_salida = os.path.join("salida", slug) if slug else "salida"
    os.makedirs(carpeta_salida, exist_ok=True)

    out_video = args.out
    if not out_video:
        out_video = os.path.join(carpeta_salida, f"preview_{args.composicion}.mp4")

    ruta_remotion = os.path.abspath("remotion")
    ruta_salida_abs = os.path.abspath(out_video).replace("\\", "/")

    cmd = [
        "npx", "remotion", "render",
        args.composicion,
        ruta_salida_abs,
        f"--scale={args.scale}",
        f"--crf={args.crf}",
        "--overwrite"
    ]

    if args.props:
        cmd.append(f"--props={args.props}")

    print(f"\n=== PRERENDERIZADO RÁPIDO (PREVIEW) ===")
    print(f"Composición : {args.composicion}")
    print(f"Escala      : {args.scale}x (540x960)")
    print(f"Salida      : {out_video}")
    print(f"Lanzando render ultrarrápido en Remotion...")

    t_start = time.time()
    subprocess.run(cmd, cwd=ruta_remotion, shell=True, check=True)
    t_total = time.time() - t_start

    tam_mb = os.path.getsize(out_video) / (1024 * 1024) if os.path.exists(out_video) else 0

    print(f"\n Preview generado con éxito:")
    print(f"  ├─ Tiempo de render : {t_total:.1f} segundos")
    print(f"  ├─ Tamaño archivo   : {tam_mb:.2f} MB")
    print(f"  └─ Ubicación        : {out_video}\n")

if __name__ == "__main__":
    main()
