import json
import os
import subprocess
import numpy as np
from faster_whisper import WhisperModel

video_path = "salida/2026_11_23_falta_de_contexto/contexto1.mp4"
print(f"Extrayendo audio PCM de {video_path}...")

cmd = [
    "ffmpeg", "-v", "error", "-i", video_path,
    "-f", "s16le", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-"
]
pcm_data = subprocess.check_output(cmd)
audio_arr = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0

print("Cargando modelo Whisper 'small' para transcripción precisa palabra por palabra...")
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    audio_arr,
    language="es",
    word_timestamps=True,
    initial_prompt="Edson Moisés Silva Cárdenas, desarrollo de software, inteligencia artificial, arquitectura, delegando código a la IA sin contexto, MLGens, producción."
)

words_list = []
segments_list = []
full_text = []

for seg_idx, segment in enumerate(segments, 1):
    seg_words = []
    full_text.append(segment.text.strip())
    for w in (segment.words or []):
        word_clean = w.word.strip()
        word_obj = {
            "word": word_clean,
            "start": round(w.start, 2),
            "end": round(w.end, 2),
            "start_frame": int(round(w.start * 30)),
            "end_frame": int(round(w.end * 30)),
            "probability": round(w.probability, 3)
        }
        words_list.append(word_obj)
        seg_words.append(word_obj)

    segments_list.append({
        "id": seg_idx,
        "start": round(segment.start, 2),
        "end": round(segment.end, 2),
        "start_frame": int(round(segment.start * 30)),
        "end_frame": int(round(segment.end * 30)),
        "text": segment.text.strip(),
        "words": seg_words
    })

result = {
    "video": video_path,
    "fps": 30,
    "duration_seconds": round(len(audio_arr) / 16000.0, 2),
    "total_words": len(words_list),
    "full_text": " ".join(full_text),
    "segments": segments_list,
    "words": words_list
}

# Guardar en salida, insumos y remotion/public
destinos = [
    "salida/2026_11_23_falta_de_contexto/transcripcion_contexto1.json",
    "insumos/2026_11_23_falta_de_contexto/transcripcion_contexto1.json",
    "remotion/public/2026_11_23_falta_de_contexto/subtitulos_contexto1.json"
]

for d in destinos:
    os.makedirs(os.path.dirname(d), exist_ok=True)
    with open(d, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Guardado en: {d}")

print(f"\nTranscripción completada con éxito. Total palabras: {len(words_list)}")
print(f"Texto completo:\n{result['full_text']}")
