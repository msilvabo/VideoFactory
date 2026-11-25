import argparse
import glob
import json
import os
import subprocess
from PIL import Image

IGNORAR_PREFIJOS = ("temp_", "guion-", "escena-", "plan")

def asegurar_estructura_proyecto(proyecto: str):
    rutas = {
        "insumos": os.path.join("insumos", proyecto),
        "salida": os.path.join("salida", proyecto),
        "public": os.path.join("remotion", "public", proyecto),
    }
    for clave, ruta in rutas.items():
        os.makedirs(ruta, exist_ok=True)
    return rutas

def obtener_info_media(ruta: str):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration:stream=width,height,codec_type",
        "-of", "json", ruta
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(res.stdout)
        duracion = round(float(data.get("format", {}).get("duration", 0)), 2)
        streams = data.get("streams", [])
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        tiene_audio = any(s.get("codec_type") == "audio" for s in streams)
        return {
            "duracion_seg": duracion,
            "resolucion": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
            "tiene_audio": tiene_audio
        }
    except Exception:
        return {"duracion_seg": 0, "resolucion": "N/A", "tiene_audio": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proyecto", required=True, help="Nombre del proyecto (ej. code-cats)")
    args = parser.parse_args()

    rutas = asegurar_estructura_proyecto(args.proyecto)
    carpeta_insumos = rutas["insumos"]

    archivos = sorted(glob.glob(os.path.join(carpeta_insumos, "*.*")))
    inventario = {
        "proyecto": args.proyecto,
        "rutas_creadas": rutas,
        "resumen": {"total_videos": 0, "total_fotos": 0, "total_audios": 0},
        "videos": [],
        "fotos": [],
        "audios": []
    }

    for ruta in archivos:
        nombre = os.path.basename(ruta)
        if nombre.lower().startswith(IGNORAR_PREFIJOS):
            continue

        ext = os.path.splitext(ruta)[1].lower()

        if ext in [".mp4", ".mov", ".webm", ".mkv"]:
            info = obtener_info_media(ruta)
            inventario["videos"].append({"archivo": nombre, **info})
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            try:
                with Image.open(ruta) as img:
                    w, h = img.size
                    res_img = f"{w}x{h}"
            except Exception:
                res_img = "N/A"
            inventario["fotos"].append({"archivo": nombre, "resolucion": res_img})
        elif ext in [".mp3", ".wav", ".m4a", ".ogg"]:
            info = obtener_info_media(ruta)
            inventario["audios"].append({"archivo": nombre, "duracion_seg": info["duracion_seg"]})

    inventario["resumen"]["total_videos"] = len(inventario["videos"])
    inventario["resumen"]["total_fotos"] = len(inventario["fotos"])
    inventario["resumen"]["total_audios"] = len(inventario["audios"])

    print(json.dumps(inventario, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()