import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
import numpy as np
from faster_whisper import WhisperModel

def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    texto = re.sub(r"[-\s]+", "_", texto)
    return texto or "proyecto_sin_nombre"

def transcribir_dialogo(video_path: str):
    print(f"Analizando diálogo con Faster-Whisper...")
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-i", video_path,
        "-f", "s16le", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", "-"
    ]
    raw = subprocess.check_output(cmd)
    data = np.frombuffer(raw, np.int16).flatten().astype(np.float32) / 32768.0

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(data, language="es", word_timestamps=True)

    frases = []
    texto_completo = []
    for s in segments:
        frases.append({
            "start": round(s.start, 2),
            "end": round(s.end, 2),
            "texto": s.text.strip()
        })
        texto_completo.append(s.text.strip())

    return frases, " ".join(texto_completo)

def inferir_animacion_educativa(frases, texto_completo):
    """
    Analiza semánticamente el diálogo y propone la escena gráfica puramente visual (cero texto).
    """
    texto_lower = texto_completo.lower()
    print(f"\nTexto detectado: \"{texto_completo}\"")

    # Caso 1: Falta de contexto / Problemas de código con IA
    if "contexto" in texto_lower or "código" in texto_lower or "problema" in texto_lower:
        # Encontrar en qué segundo se menciona "contexto" o "problema"
        start_impacto = 1.5
        duracion = 5.8
        for f in frases:
            if "contexto" in f["texto"].lower() or "problema" in f["texto"].lower():
                start_impacto = max(0.8, f["start"] - 0.8)
                duracion = max(4.0, f["end"] - start_impacto + 1.2)
                break

        animacion = {
            "escena": "context_break",
            "posicion": "top",
            "metáfora": "Chip acelerado + Cable desconectado con chispas + Alerta pulsante",
            "startSec": round(start_impacto, 2),
            "durationSec": round(duracion, 2),
            "startFrame": int(start_impacto * 30),
            "durationFrames": int(duracion * 30)
        }
        return animacion

    # Caso 2: Por defecto / Flujo de Datos
    dur_total = frases[-1]["end"] if frases else 6.0
    return {
        "escena": "pipeline",
        "posicion": "top",
        "metáfora": "Flujo de datos y nodos interconectados",
        "startSec": 1.0,
        "durationSec": round(dur_total - 1.0, 2),
        "startFrame": 30,
        "durationFrames": int((dur_total - 1.0) * 30)
    }

def main():
    parser = argparse.ArgumentParser(description="Analizador de diálogo y generador de animaciones técnicas educativas")
    parser.add_argument("--video", required=True, help="Ruta al video (ej. insumos/.../inicio1_limpio_sinPausas.mp4)")
    parser.add_argument("--proyecto", default="", help="Slug del proyecto (opcional)")
    parser.add_argument("--tipo", choices=["tarjeta", "pasos", "comparacion", "codigo"], help="Sobrescribir tipo de plantilla")
    parser.add_argument("--posicion", choices=["top", "bottom"], help="Posición: top o bottom")
    parser.add_argument("--titulo", help="Sobrescribir título")
    parser.add_argument("--items", help="Viñetas separadas por coma")
    parser.add_argument("--render_preview", action="store_true", default=True, help="Genera preview MP4 de la animación")

    args = parser.parse_args()

    if not os.path.exists(args.video):
        print(f"Error: No existe el video '{args.video}'")
        sys.exit(1)

    # 1. Transcribir diálogo
    frases, texto_completo = transcribir_dialogo(args.video)

    # 2. Inferir animación
    anim = inferir_animacion_educativa(frases, texto_completo)

    # Sobreescrituras si el usuario especificó argumentos CLI
    if args.posicion:
        anim["posicion"] = args.posicion

    dir_video = os.path.dirname(args.video)
    nombre_video = os.path.splitext(os.path.basename(args.video))[0]
    json_salida = os.path.join(dir_video, f"animacion_{nombre_video}.json")

    with open(json_salida, "w", encoding="utf-8") as f:
        json.dump(anim, f, indent=2, ensure_ascii=False)

    print(f"\n ANIMACIÓN GRÁFICA SIMBÓLICA (100% VISUAL, CERO TEXTO):")
    print(f"  ├─ Escena    : {anim['escena'].upper()} ({anim['posicion'].upper()})")
    print(f"  ├─ Metáfora  : {anim['metáfora']}")
    print(f"  ├─ Tiempo    : Segundo {anim['startSec']}s a {anim['startSec'] + anim['durationSec']}s ({anim['durationFrames']} frames)")
    print(f"  └─ Config    : {json_salida}")

    # 3. Renderizar preview en baja resolución para aprobación
    if args.render_preview:
        carpeta_salida = dir_video.replace("insumos", "salida")
        os.makedirs(carpeta_salida, exist_ok=True)
        preview_out = os.path.join(carpeta_salida, f"preview_anim_visual_{nombre_video}.png")

        print(f"\nRenderizando fotograma de previsualización en Remotion...")
        ruta_props_abs = os.path.abspath(json_salida).replace("\\", "/")
        ruta_salida_abs = os.path.abspath(preview_out).replace("\\", "/")
        frame_target = min(280, max(20, int(anim['startFrame'] + 20)))

        cmd_still = [
            "npx", "remotion", "still",
            "TechAnimationPreview",
            ruta_salida_abs,
            f"--props={ruta_props_abs}",
            f"--frame={frame_target}",
            "--overwrite"
        ]
        subprocess.run(cmd_still, cwd=os.path.abspath("remotion"), shell=True, check=True)
        print(f" Previsualización visual generada en: {preview_out}\n")

if __name__ == "__main__":
    main()
