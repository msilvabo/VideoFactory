import argparse
import json
import os
import shutil
import subprocess
import numpy as np
from faster_whisper import WhisperModel


def asegurar_carpetas(proyecto: str):
    rutas = {
        "insumos": os.path.join("insumos", proyecto) if proyecto else "insumos",
        "salida": os.path.join("salida", proyecto) if proyecto else "salida",
        "public": os.path.join("remotion", "public", proyecto) if proyecto else os.path.join("remotion", "public"),
    }
    for r in rutas.values():
        os.makedirs(r, exist_ok=True)
    return rutas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proyecto", default="", help="Nombre del proyecto (ej. code-cats)")
    parser.add_argument("--video", required=False, help="Ruta al video crudo de cámara")
    parser.add_argument("--audio", required=True, help="Ruta al audio limpio (.mp3/.wav o .mp4)")
    parser.add_argument("--out_video", default="", help="Ruta opcional de salida del video sincronizado")
    parser.add_argument("--out_subs", default="", help="Ruta opcional de salida del JSON de subtítulos")
    args = parser.parse_args()

    # 0. Crear estructura de carpetas del proyecto automáticamente
    rutas = asegurar_carpetas(args.proyecto)

    out_video = args.out_video or os.path.join(rutas["public"], "video_sync.mp4")
    out_subs = args.out_subs or os.path.join(rutas["public"], "subtitulos.json")

    os.makedirs(os.path.dirname(os.path.abspath(out_video)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(out_subs)), exist_ok=True)

    # Copiar también el audio limpio a remotion/public/<proyecto>/ para que Remotion pueda leerlo con staticFile
    nombre_audio = os.path.basename(args.audio)
    destino_audio_public = os.path.join(rutas["public"], nombre_audio)
    if os.path.abspath(args.audio) != os.path.abspath(destino_audio_public):
        shutil.copy2(args.audio, destino_audio_public)

    # 1. Si hay video y audio separados, sincronizar por forma de onda (claqueta/aplauso)
    if args.video:
        res = subprocess.check_output(
            [".venv/Scripts/audio-offset-finder", "--find-offset-of", args.audio, "--within", args.video],
            text=True
        )
        offset = float([line.split(":")[1].strip() for line in res.splitlines() if "Offset" in line][0])
        print(f"OFFSET_DETECTADO={offset}")

        if offset >= 0:
            cmd = [
                "ffmpeg", "-y", "-ss", str(offset), "-i", args.video,
                "-i", args.audio, "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", out_video
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-i", args.video,
                "-ss", str(abs(offset)), "-i", args.audio,
                "-c:v", "libx264", "-preset", "fast",
                "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", out_video
            ]
        subprocess.run(cmd, check=True)

    # 2. Transcribir con Faster-Whisper (timestamps palabra por palabra)
    cmd = [
        "ffmpeg", "-y", "-i", args.audio,
        "-f", "s16le", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", "-"
    ]
    audio_bytes = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
    audio_data = np.frombuffer(audio_bytes, np.int16).flatten().astype(np.float32) / 32768.0

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_data, language="es", word_timestamps=True)

    words_data = []
    for seg in segments:
        for w in seg.words:
            words_data.append({
                "word": w.word.strip(),
                "start": round(w.start, 3),
                "end": round(w.end, 3)
            })

    with open(out_subs, "w", encoding="utf-8") as f:
        json.dump(words_data, f, ensure_ascii=False, indent=2)

    print(f"PROYECTO={args.proyecto or 'raiz'}")
    print(f"RUTA_SUBTITULOS={out_subs}")
    print(f"SUBTITULOS_GENERADOS={len(words_data)} palabras")


if __name__ == "__main__":
    main()