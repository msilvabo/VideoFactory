import argparse
import os
import subprocess
import time
import numpy as np
from PIL import Image
from rembg import new_session, remove

def main():
    parser = argparse.ArgumentParser(description="Extrae la silueta del presentador con canal alfa en formato WebM (VP9 yuva420p)")
    parser.add_argument("--video", "-v", required=True, help="Ruta al video de entrada")
    parser.add_argument("--out", "-o", required=True, help="Ruta al archivo WebM de salida")
    parser.add_argument("--fps", type=int, default=30, help="FPS del video")
    parser.add_argument("--model", default="u2netp", help="Modelo de rembg (def: u2netp)")
    parser.add_argument("--max_frames", type=int, default=0, help="Límite opcional de frames (0 = todos)")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    # Duración y total frames
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", args.video
    ]
    duration = float(subprocess.check_output(probe_cmd, text=True).strip())
    total_frames = int(duration * args.fps)
    if args.max_frames > 0:
        total_frames = min(total_frames, args.max_frames)

    width, height = 1080, 1920
    frame_bytes_rgb = width * height * 3

    print(f"\n=== SEGMENTACIÓN DE SILUETA (CANAL ALFA) ===")
    print(f"Video entrada : {args.video} ({duration:.2f}s, ~{total_frames} frames a {args.fps}fps)")
    print(f"Salida WebM   : {args.out}")
    print(f"Modelo rembg  : {args.model}")

    session = new_session(args.model)

    ffmpeg_in_cmd = [
        "ffmpeg", "-v", "error", "-i", args.video,
        "-vf", f"fps={args.fps},scale={width}:{height}",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ]
    pipe_in = subprocess.Popen(ffmpeg_in_cmd, stdout=subprocess.PIPE, bufsize=frame_bytes_rgb * 10)

    ffmpeg_out_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{width}x{height}", "-pix_fmt", "rgba",
        "-r", str(args.fps), "-i", "-",
        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
        "-b:v", "0", "-crf", "24", "-speed", "4",
        args.out
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

            frame_arr = np.frombuffer(raw_frame, dtype=np.uint8).reshape((height, width, 3))
            frame_img = Image.fromarray(frame_arr)

            # Segmentación pura con rembg
            segmented = remove(frame_img, session=session)
            rgba_bytes = segmented.tobytes()
            pipe_out.stdin.write(rgba_bytes)

            if frame_idx % 20 == 0 or frame_idx == total_frames:
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

    t_total = time.time() - t_start
    print(f"\n Segmentación completada:")
    print(f"  ├─ Frames procesados: {frame_idx}")
    print(f"  ├─ Tiempo total     : {t_total:.1f}s")
    print(f"  └─ Archivo WebM     : {args.out}\n")

if __name__ == "__main__":
    main()
