import json
import subprocess
import numpy as np
from faster_whisper import WhisperModel

audio_path = "insumos/2026_11_23_falta_de_contexto/medio_2_limpio_sinPausas.mp4"

cmd = [
    "ffmpeg", "-v", "error", "-i", audio_path,
    "-f", "s16le", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", "-"
]
pcm_data = subprocess.check_output(cmd)
audio_arr = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe(audio_arr, language="es", word_timestamps=True)

words_list = []
full_text = []
for segment in segments:
    full_text.append(segment.text)
    for w in segment.words:
        words_list.append({
            "word": w.word.strip(),
            "start": round(w.start, 2),
            "end": round(w.end, 2),
            "start_frame": int(round(w.start * 30)),
            "end_frame": int(round(w.end * 30)),
        })

result = {
    "text": "".join(full_text).strip(),
    "words": words_list
}

with open("insumos/2026_11_23_falta_de_contexto/transcripcion_medio_2.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(json.dumps(result, indent=2, ensure_ascii=False))
