import argparse
import asyncio
import os
import shutil
import subprocess
import edge_tts

VOCES = {
    "grave": "es-MX-JorgeNeural",
    "profunda": "es-ES-AlvaroNeural",
    "neutral": "es-BO-MarceloNeural",
    "femenina": "es-MX-DaliaNeural"
}


def asegurar_carpetas(proyecto: str):
    rutas = {
        "insumos": os.path.join("insumos", proyecto) if proyecto else "insumos",
        "salida": os.path.join("salida", proyecto) if proyecto else "salida",
        "public": os.path.join("remotion", "public", proyecto) if proyecto else os.path.join("remotion", "public"),
    }
    for r in rutas.values():
        os.makedirs(r, exist_ok=True)
    return rutas


async def generar_base(texto: str, voz: str, archivo_temp: str, velocidad: str, tono: str):
    # Añadimos un pequeño silencio al final con puntuación para evitar que corte la última sílaba
    texto_seguro = texto.strip() + " ..."
    communicate = edge_tts.Communicate(texto_seguro, voz, rate=velocidad, pitch=tono)
    await communicate.save(archivo_temp)


def aplicar_efecto_ffmpeg(entrada: str, salida: str, estilo: str):
    if estilo == "robot":
        # Robot de videojuego claro: respeta el sample rate original,
        # aplica vibración cibernética limpia (tremolo) y resonancia de chasis metálico corto (15ms)
        filtro = (
            "aresample=44100,"
            "tremolo=f=45:d=0.35,"
            "aecho=0.8:0.85:15:0.35,"
            "highpass=f=180,"
            "equalizer=f=2500:width_type=h:width=500:g=4,"
            "apad=pad_dur=0.25"
        )
    elif estilo == "doom":
        # Voz grave e imponente sin perder dicción (baja tono sin acelerar sample rate)
        filtro = (
            "aresample=44100,"
            "asetrate=44100*0.90,aresample=44100,atempo=1.08,"
            "aecho=0.8:0.85:22:0.3,"
            "equalizer=f=140:width_type=h:width=100:g=5,"
            "equalizer=f=3000:width_type=h:width=400:g=3,"
            "apad=pad_dur=0.25"
        )
    else:
        filtro = "apad=pad_dur=0.25"

    cmd = [
        "ffmpeg", "-y", "-i", entrada,
        "-af", filtro,
        "-c:a", "libmp3lame", "-q:a", "2", salida
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Generar voz neuronal con edge-tts y filtros FFmpeg")
    parser.add_argument("--texto", required=True, help="Texto a sintetizar")
    parser.add_argument("--voz", default="neutral", choices=list(VOCES.keys()), help="Estilo o género de voz")
    parser.add_argument("--velocidad", default="+0%", help="Aceleración (ej. +10%%, -5%%)")
    parser.add_argument("--tono", default="+0Hz", help="Afinación de tono (ej. +5Hz, -10Hz)")
    parser.add_argument("--estilo", default="", choices=["", "robot", "doom"], help="Efecto o filtro FFmpeg")
    parser.add_argument("--proyecto", default="", help="Slug del proyecto opcional")
    parser.add_argument("--out", default="", help="Ruta de salida del audio generado (.mp3)")
    args = parser.parse_args()

    rutas = asegurar_carpetas(args.proyecto)
    ruta_salida = args.out
    if not ruta_salida:
        nombre = f"locucion_{args.voz}.mp3"
        ruta_salida = os.path.join(rutas["insumos"], nombre)

    os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)

    voz_id = VOCES.get(args.voz, VOCES["neutral"])
    temp_file = ruta_salida + ".temp.mp3"

    try:
        asyncio.run(generar_base(args.texto, voz_id, temp_file, args.velocidad, args.tono))
        if args.estilo:
            aplicar_efecto_ffmpeg(temp_file, ruta_salida, args.estilo)
        else:
            if os.path.exists(ruta_salida):
                os.remove(ruta_salida)
            os.rename(temp_file, ruta_salida)
        print(f"AUDIO_GENERADO={ruta_salida}")
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except OSError:
                pass


if __name__ == "__main__":
    main()
