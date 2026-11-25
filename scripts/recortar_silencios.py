import argparse
import json
import os
import re
import subprocess
import sys
import numpy as np
from pydub import AudioSegment, silence
from faster_whisper import WhisperModel

MULETILLAS_DEFECTO = [
    "eh", "ehh", "ehhh", "em", "emm", "mmm", "mm", "uh", "uhh", "ah", "ahh",
    "aj", "este", "o sea", "bueno"
]

def normalizar_palabra(p: str) -> str:
    return re.sub(r"[^\w\s]", "", p).strip().lower()

def detectar_muletillas_whisper(audio_path, palabras_muletilla=None):
    """
    Usa Faster-Whisper para obtener palabras con timestamps e identifica las muletillas.
    Retorna una lista de intervalos a excluir: [{"start": float, "end": float, "word": str}]
    """
    if palabras_muletilla is None:
        palabras_muletilla = MULETILLAS_DEFECTO

    print(f"Analizando muletillas y habla con Faster-Whisper...")

    # Extraer PCM 16kHz para Whisper
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", audio_path,
        "-f", "s16le", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", "-"
    ]
    audio_bytes = subprocess.check_output(cmd)
    audio_data = np.frombuffer(audio_bytes, np.int16).flatten().astype(np.float32) / 32768.0

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_data, language="es", word_timestamps=True)

    muletillas_detectadas = []
    total_palabras = 0

    for seg in segments:
        for w in seg.words:
            total_palabras += 1
            palabra_limpia = normalizar_palabra(w.word)
            if palabra_limpia in palabras_muletilla:
                # Agregar pequeño margen (50ms) para corte quirúrgico
                start_corte = max(0.0, round(w.start - 0.05, 3))
                end_corte = round(w.end + 0.05, 3)
                muletillas_detectadas.append({
                    "start": start_corte,
                    "end": end_corte,
                    "word": w.word.strip()
                })

    print(f"Palabras transcritas: {total_palabras} | Muletillas detectadas: {len(muletillas_detectadas)}")
    if muletillas_detectadas:
        muestras = [f"'{m['word']}' ({m['start']}s-{m['end']}s)" for m in muletillas_detectadas[:5]]
        print(f"Ejemplos de muletillas: {', '.join(muestras)}{'...' if len(muletillas_detectadas) > 5 else ''}")

    return muletillas_detectadas

def sustraer_intervalos(tramos_hablados, intervalos_excluir):
    """
    Resta los intervalos de muletillas de los tramos de audio hablado.
    """
    if not intervalos_excluir:
        return tramos_hablados

    resultado = []
    for tramo in tramos_hablados:
        cur_start = tramo["start"]
        cur_end = tramo["end"]

        # Encontrar exclusiones que caigan dentro de este tramo
        cortes = [e for e in intervalos_excluir if e["end"] > cur_start and e["start"] < cur_end]
        cortes.sort(key=lambda x: x["start"])

        for c in cortes:
            excl_start = max(cur_start, c["start"])
            excl_end = min(cur_end, c["end"])

            if excl_start > cur_start + 0.15:  # conservar si queda al menos 150ms
                resultado.append({"start": round(cur_start, 3), "end": round(excl_start, 3)})

            cur_start = max(cur_start, excl_end)

        if cur_end > cur_start + 0.15:
            resultado.append({"start": round(cur_start, 3), "end": round(cur_end, 3)})

    return resultado

def detectar_tramos_hablados(audio_path, min_silence_len=350, silence_thresh=-35, keep_silence=120):
    audio = AudioSegment.from_file(audio_path)
    duracion_original = len(audio) / 1000.0

    nonsilent_ranges = silence.detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )

    tramos = []
    for start_ms, end_ms in nonsilent_ranges:
        start_sec = max(0.0, (start_ms - keep_silence) / 1000.0)
        end_sec = min(duracion_original, (end_ms + keep_silence) / 1000.0)
        tramos.append({"start": round(start_sec, 3), "end": round(end_sec, 3)})

    # Unir solapados
    tramos_unidos = []
    for t in tramos:
        if not tramos_unidos:
            tramos_unidos.append(t)
        else:
            prev = tramos_unidos[-1]
            if t["start"] <= prev["end"]:
                prev["end"] = max(prev["end"], t["end"])
            else:
                tramos_unidos.append(t)

    return tramos_unidos, duracion_original

def aplicar_cortes_video(video_path, tramos, out_path):
    if not tramos:
        print("No se encontraron tramos de audio validos.")
        return

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    filter_parts = []
    concat_inputs = []

    for idx, t in enumerate(tramos):
        start = t["start"]
        end = t["end"]
        filter_parts.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{idx}];")
        filter_parts.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{idx}];")
        concat_inputs.append(f"[v{idx}][a{idx}]")

    num_tramos = len(tramos)
    filter_parts.append(f"{''.join(concat_inputs)}concat=n={num_tramos}:v=1:a=1[outv][outa]")
    filter_complex = "".join(filter_parts)

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        out_path
    ]

    print("Renderizando video con cortes dinámicos (FFmpeg concat)...")
    subprocess.run(cmd, check=True)
    print(f" Video final generado en: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Detector y cortador automático de silencios y muletillas (_sinPausas)")
    parser.add_argument("--video", required=True, help="Ruta al video")
    parser.add_argument("--out", default="", help="Ruta de salida (por defecto: <nombre>_sinPausas.mp4)")
    parser.add_argument("--sin_muletillas", action="store_true", default=True, help="Eliminar muletillas con Whisper (activo por defecto)")
    parser.add_argument("--solo_silencios", action="store_true", help="Solo cortar silencios sin analizar muletillas")
    parser.add_argument("--muletillas", default="", help="Palabras adicionales de muletilla separadas por coma")
    parser.add_argument("--min_silence", type=int, default=350, help="Minimo silencio en ms (def: 350)")
    parser.add_argument("--threshold", type=int, default=-35, help="Umbral de silencio en dBFS (def: -35)")
    parser.add_argument("--keep_silence", type=int, default=120, help="Colchón en ms (def: 120)")
    parser.add_argument("--solo_json", action="store_true", help="Solo genera JSON sin renderizar video")

    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"Error: No existe el archivo de video: {args.video}")
        sys.exit(1)

    # Determinar nombre de salida con sufijo _sinPausas
    out_video = args.out
    if not out_video and not args.solo_json:
        dir_name = os.path.dirname(args.video)
        base, ext = os.path.splitext(os.path.basename(args.video))
        out_video = os.path.join(dir_name, f"{base}_sinPausas{ext}")

    print(f"\n=== CORTE AUTOMÁTICO DE SILENCIOS Y MULETILLAS ===")
    print(f"Entrada : {args.video}")
    if out_video:
        print(f"Salida  : {out_video}")

    # 1. Detectar silencios
    tramos_hablados, dur_orig = detectar_tramos_hablados(
        args.video,
        min_silence_len=args.min_silence,
        silence_thresh=args.threshold,
        keep_silence=args.keep_silence
    )

    # 2. Detectar y restar muletillas si está habilitado
    tramos_finales = tramos_hablados
    if not args.solo_silencios:
        lista_m = list(MULETILLAS_DEFECTO)
        if args.muletillas:
            lista_m.extend([m.strip().lower() for m in args.muletillas.split(",") if m.strip()])

        intervalos_muletillas = detectar_muletillas_whisper(args.video, palabras_muletilla=lista_m)
        tramos_finales = sustraer_intervalos(tramos_hablados, intervalos_muletillas)

    dur_util = sum(t["end"] - t["start"] for t in tramos_finales)
    tiempo_ahorrado = dur_orig - dur_util
    pct_ahorro = (tiempo_ahorrado / dur_orig) * 100 if dur_orig > 0 else 0

    print(f"\nResumen de optimización:")
    print(f"  ├─ Duración original : {dur_orig:.2f}s")
    print(f"  ├─ Duración final    : {dur_util:.2f}s")
    print(f"  ├─ Tiempo eliminado  : {tiempo_ahorrado:.2f}s ({pct_ahorro:.1f}%)")
    print(f"  └─ Tramos de voz     : {len(tramos_finales)}")

    if not args.solo_json and out_video:
        aplicar_cortes_video(args.video, tramos_finales, out_video)

if __name__ == "__main__":
    main()
