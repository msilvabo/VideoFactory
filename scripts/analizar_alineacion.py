import subprocess
import numpy as np
from faster_whisper import WhisperModel

def get_detailed_words(file_path):
    cmd = ['ffmpeg', '-v', 'error', '-i', file_path, '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-']
    pcm = subprocess.check_output(cmd)
    arr = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    model = WhisperModel('base', device='cpu', compute_type='int8')
    segs, info = model.transcribe(arr, language='es', word_timestamps=True)
    words = []
    for s in segs:
        for w in s.words:
            words.append({'word': w.word.strip(), 'start': w.start, 'end': w.end})
    return info.duration, words

dur1, w1 = get_detailed_words('insumos/2026_11_23_falta_de_contexto/medio.mp3')
dur2, w2 = get_detailed_words('insumos/2026_11_23_falta_de_contexto/medio_2_limpio_sinPausas.mp4')

print(f"=== MEDIO.MP3 (dur={dur1:.2f}s) ===")
for w in w1:
    print(f"  {w['start']:5.2f}s - {w['end']:5.2f}s : {w['word']}")

print(f"\n=== VIDEO MEDIO_2 (dur={dur2:.2f}s) ===")
for w in w2:
    print(f"  {w['start']:5.2f}s - {w['end']:5.2f}s : {w['word']}")
