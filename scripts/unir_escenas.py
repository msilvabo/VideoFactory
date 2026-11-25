import argparse
import glob
import os
import subprocess


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proyecto", required=True, help="Nombre del proyecto (ej. code-cats)")
    parser.add_argument("--volumen_musica", type=float, default=0.14, help="Volumen de la música de fondo (0.0 a 1.0)")
    args = parser.parse_args()

    carpeta_salida = os.path.join("salida", args.proyecto)
    carpeta_insumos = os.path.join("insumos", args.proyecto)
    os.makedirs(carpeta_salida, exist_ok=True)

    # Buscar todas las escenas renderizadas en orden (escena-01.mp4, escena-02.mp4...)
    patron = os.path.join(carpeta_salida, "escena-*.mp4")
    escenas = sorted(glob.glob(patron))

    if not escenas:
        raise SystemExit(f"ERROR: No se encontraron archivos escena-XX.mp4 en {carpeta_salida}")

    lista_txt = os.path.join(carpeta_salida, "lista_concat.txt")
    with open(lista_txt, "w", encoding="utf-8") as f:
        for esc in escenas:
            ruta_abs = os.path.abspath(esc).replace("\\", "/")
            f.write(f"file '{ruta_abs}'\n")

    video_unido_temp = os.path.join(carpeta_salida, "temp_unido.mp4")
    video_final = os.path.join(carpeta_salida, f"{args.proyecto}_final.mp4")

    # 1. Concatenar todas las escenas normalizando a 30fps / 1080x1920 / AAC
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista_txt,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        video_unido_temp
    ]
    subprocess.run(cmd_concat, check=True)

    # 2. Si existe musica_fondo.mp3 en insumos/<proyecto>/, mezclarla de fondo
    musica_fondo = os.path.join(carpeta_insumos, "musica_fondo.mp3")
    if os.path.exists(musica_fondo):
        filtro = (
            f"[1:a]volume={args.volumen_musica}[bg];"
            f"[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        cmd_musica = [
            "ffmpeg", "-y",
            "-i", video_unido_temp,
            "-stream_loop", "-1", "-i", musica_fondo,
            "-filter_complex", filtro,
            "-map", "0:v:0", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            video_final
        ]
        subprocess.run(cmd_musica, check=True)
        os.remove(video_unido_temp)
    else:
        if os.path.exists(video_final):
            os.remove(video_final)
        os.rename(video_unido_temp, video_final)

    if os.path.exists(lista_txt):
        os.remove(lista_txt)

    print(f"ESCENAS_UNIDAS={len(escenas)}")
    print(f"VIDEO_FINAL_OK={video_final}")


if __name__ == "__main__":
    main()