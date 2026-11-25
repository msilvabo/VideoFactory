import argparse
import json
import os
import subprocess
import numpy as np


def extraer_envolvente_rms(audio_path: str, fps: int = 30) -> list[float]:
    """
    Decodifica el audio mediante FFmpeg a PCM 16-bit 48kHz mono y calcula
    la amplitud RMS por fotograma (normalizada de 0.05 a 1.0).
    """
    sample_rate = 48000
    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-f", "s16le", "-acodec", "pcm_s16le",
        "-ar", str(sample_rate), "-ac", "1", "-"
    ]
    audio_bytes = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
    samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

    samples_per_frame = int(sample_rate / fps)
    total_frames = len(samples) // samples_per_frame

    waveform = []
    for f in range(total_frames):
        chunk = samples[f * samples_per_frame : (f + 1) * samples_per_frame]
        rms = np.sqrt(np.mean(chunk**2)) if len(chunk) > 0 else 0.0
        waveform.append(float(rms))

    if not waveform:
        return [0.1] * 30

    max_val = max(waveform)
    if max_val > 0:
        # Normalizar con compresión para visualización estética
        normalized = [round(min(1.0, max(0.08, float(val / max_val))), 3) for val in waveform]
    else:
        normalized = [0.1] * len(waveform)

    return normalized


def main():
    parser = argparse.ArgumentParser(description="Extrae la envolvente de audio por fotograma para Remotion")
    parser.add_argument("--audio", required=True, help="Ruta al archivo de audio o video")
    parser.add_argument("--proyecto", default="", help="Slug del proyecto (guarda en remotion/public/<proyecto>/waveform.json)")
    parser.add_argument("--out", default="", help="Ruta personalizada de salida del JSON")
    parser.add_argument("--fps", type=int, default=30, help="Fotogramas por segundo del video (por defecto 30)")
    args = parser.parse_args()

    ruta_salida = args.out
    if not ruta_salida:
        if args.proyecto:
            ruta_salida = os.path.join("remotion", "public", args.proyecto, "waveform.json")
        else:
            base = os.path.splitext(args.audio)[0]
            ruta_salida = f"{base}_waveform.json"

    os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)

    valores = extraer_envolvente_rms(args.audio, args.fps)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(valores, f, indent=2)

    print(f"AUDIO_ENVELOPE_OK={ruta_salida}")
    print(f"TOTAL_FOTOGRAMAS={len(valores)}")


if __name__ == "__main__":
    main()
