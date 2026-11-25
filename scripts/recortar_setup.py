import argparse
import os
import subprocess
import time
import numpy as np
from PIL import Image, ImageDraw
from rembg import new_session, remove

def build_static_mask(width=1080, height=1920):
    mask_img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask_img)
    # 1. Left monitor and left desk (x: 0..480, y: 1260..1920)
    draw.rectangle([0, 1260, 480, height], fill=255)
    # 2. Right monitor (x: 850..1080, y: 1020..height)
    draw.rectangle([850, 1020, width, height], fill=255)
    # 3. Full lower desk across entire screen (y: 1340..height)
    draw.rectangle([0, 1340, width, height], fill=255)
    return np.array(mask_img)

def main():
    parser = argparse.ArgumentParser(description="Recorta primer plano con canal alfa combinando rembg y mascara geometrica")
    parser.add_argument("--proyecto", default="dooms_inicio", help="Nombre del proyecto")
    parser.add_argument("--video", default="insumos/dooms_inicio/taller.mp4", help="Ruta al video de entrada")
    parser.add_argument("--out", default="", help="Ruta de salida del video webm")
    parser.add_argument("--fps", type=int, default=30, help="FPS del video de salida")
    parser.add_argument("--model", default="u2netp", help="Modelo de rembg (u2netp o u2net)")
    parser.add_argument("--max_frames", type=int, default=0, help="Limite de frames (0 = todos)")
    args = parser.parse_args()

    out_path = args.out or os.path.join("remotion", "public", args.proyecto, "setup_recortado.webm")
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    # Obtenemos info del video con ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", args.video
    ]
    duration_str = subprocess.check_output(probe_cmd, text=True).strip()
    duration = float(duration_str)
    total_frames = int(duration * args.fps)
    if args.max_frames > 0:
        total_frames = min(total_frames, args.max_frames)

    width, height = 1080, 1920
    frame_bytes_rgb = width * height * 3

    print(f"=== INICIANDO RECORTE DE SETUP ===")
    print(f"Video entrada: {args.video} ({duration:.2f}s, ~{total_frames} frames a {args.fps}fps)")
    print(f"Salida WebM: {out_path}")
    print(f"Modelo rembg: {args.model}")

    static_mask = build_static_mask(width, height)
    session = new_session(args.model)

    # Proceso ffmpeg para leer fotogramas en RGB24
    ffmpeg_in_cmd = [
        "ffmpeg", "-v", "error", "-i", args.video,
        "-vf", f"fps={args.fps},scale={width}:{height}",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ]
    pipe_in = subprocess.Popen(ffmpeg_in_cmd, stdout=subprocess.PIPE, bufsize=frame_bytes_rgb * 10)

    # Proceso ffmpeg para codificar VP9 con canal alfa
    ffmpeg_out_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgba",
        "-r", str(args.fps), "-i", "-",
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
        "-b:v", "0", "-crf", "22", "-speed", "4",
        out_path
    ]
    pipe_out = subprocess.Popen(ffmpeg_out_cmd, stdin=subprocess.PIPE, bufsize=frame_bytes_rgb * 10)

    frame_idx = 0
    t_start = time.time()

    try:
        while True:
            raw_frame = pipe_in.stdout.read(frame_bytes_rgb)
            if not raw_frame or len(raw_frame) < frame_bytes_rgb:
                break

            frame_idx += 1
            if args.max_frames > 0 and frame_idx > args.max_frames:
                break

            # Convertir a imagen PIL
            frame_arr = np.frombuffer(raw_frame, dtype=np.uint8).reshape((height, width, 3))
            frame_img = Image.fromarray(frame_arr)

            # Segmentar con rembg
            segmented = remove(frame_img, session=session)
            seg_alpha = np.array(segmented)[:, :, 3]

            # Combinar con mascara estatica
            combined_alpha = np.maximum(seg_alpha, static_mask)

            # Construir RGBA final
            rgba = np.dstack([frame_arr, combined_alpha])
            pipe_out.stdin.write(rgba.tobytes())

            if frame_idx % 15 == 0 or frame_idx == total_frames:
                elapsed = time.time() - t_start
                fps_proc = frame_idx / elapsed if elapsed > 0 else 0
                eta = (total_frames - frame_idx) / fps_proc if fps_proc > 0 else 0
                pct = frame_idx / total_frames * 100
                print(f"Frame {frame_idx}/{total_frames} ({pct:.1f}%) - {fps_proc:.2f} fps - ETA: {eta:.1f}s")

    finally:
        pipe_in.stdout.close()
        pipe_in.wait()
        pipe_out.stdin.close()
        pipe_out.wait()

    total_time = time.time() - t_start
    print(f"Recorte completado: {frame_idx} frames en {total_time:.1f}s ({out_path})")

if __name__ == "__main__":
    main()
