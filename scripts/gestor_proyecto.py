import argparse
import glob
import json
import os
import re
import shutil
import unicodedata

def slugify(texto: str) -> str:
    """
    Convierte cualquier nombre arbitrario (ej. "video lunes parte 1", "Taller 2.0!")
    a un identificador limpio de sistema de archivos (ej. "video_lunes_parte_1").
    """
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    texto = re.sub(r"[-\s]+", "_", texto)
    return texto or "proyecto_sin_nombre"

def asegurar_carpetas_proyecto(slug: str):
    rutas = {
        "slug": slug,
        "insumos": os.path.join("insumos", slug),
        "salida": os.path.join("salida", slug),
        "public": os.path.join("remotion", "public", slug),
    }
    for clave in ("insumos", "salida", "public"):
        os.makedirs(rutas[clave], exist_ok=True)
    return rutas

def crear_plantilla_plan(ruta_insumos: str, nombre_original: str, slug: str):
    ruta_plan = os.path.join(ruta_insumos, "plan.md")
    if not os.path.exists(ruta_plan):
        contenido = f"""# Plan de Producción: {nombre_original}

- **Identificador de Proyecto:** `{slug}`
- **Ruta de Insumos:** `./insumos/{slug}/`
- **Ruta de Salida:** `./salida/{slug}/{slug}_final.mp4`
- **Ruta Remotion Public:** `./remotion/public/{slug}/`

## 1. Archivos Multimedia
- [ ] Videos de cámara (`.mp4` / `.mov`):
- [ ] Fotos / Capturas (`.png` / `.jpg`):
- [ ] Audio limpio / Locución (`.wav` / `.mp3`):

## 2. Escaleta y Estructura
- **Gancho (0-3s):** 
- **Desarrollo (3-20s):**
- **Call to Action (20-30s):**

## 3. Subtítulos y Títulos
- **Título Detrás / Inserción:** 
- **Subtítulo:** 
"""
        with open(ruta_plan, "w", encoding="utf-8") as f:
            f.write(contenido)
        return True
    return False

def listar_proyectos():
    """
    Lista todos los proyectos encontrados en insumos/ con sus estadísticas.
    """
    if not os.path.exists("insumos"):
        print("No existe la carpeta insumos/")
        return

    carpetas = [d for d in os.listdir("insumos") if os.path.isdir(os.path.join("insumos", d))]
    print(f"\n{'='*60}")
    print(f" PROYECTOS REGISTRADOS EN VIDEOFACTORY ({len(carpetas)})")
    print(f"{'='*60}")

    if not carpetas:
        print("  (No hay proyectos creados aún)")
        return

    for c in sorted(carpetas):
        ruta_ins = os.path.join("insumos", c)
        ruta_sal = os.path.join("salida", c)
        ruta_pub = os.path.join("remotion", "public", c)

        videos = len(glob.glob(os.path.join(ruta_ins, "*.mp4")) + glob.glob(os.path.join(ruta_ins, "*.mov")))
        fotos = len(glob.glob(os.path.join(ruta_ins, "*.jpg")) + glob.glob(os.path.join(ruta_ins, "*.png")))
        audios = len(glob.glob(os.path.join(ruta_ins, "*.mp3")) + glob.glob(os.path.join(ruta_ins, "*.wav")))
        renders = len(glob.glob(os.path.join(ruta_sal, "*.mp4")))

        print(f"📁 {c}")
        print(f"   ├─ Insumos : {videos} videos | {fotos} fotos | {audios} audios")
        print(f"   ├─ Salida  : {renders} renders finalizados")
        print(f"   └─ Remotion: {ruta_pub}")

    print(f"{'='*60}\n")

def mover_archivos_sueltos(slug_destino: str):
    """
    Mueve archivos multimedia sueltos en la raíz de insumos/ hacia la carpeta del proyecto.
    """
    ruta_dest = os.path.join("insumos", slug_destino)
    extensiones_validas = (".mp4", ".mov", ".mkv", ".webm", ".mp3", ".wav", ".aac", ".jpg", ".png", ".webp")
    
    movidos = 0
    for elemento in os.listdir("insumos"):
        ruta_elem = os.path.join("insumos", elemento)
        if os.path.isfile(ruta_elem) and elemento.lower().endswith(extensiones_validas):
            shutil.move(ruta_elem, os.path.join(ruta_dest, elemento))
            movidos += 1
            print(f"  [MOVIDO] {elemento} -> insumos/{slug_destino}/{elemento}")

    if movidos > 0:
        print(f"Total archivos movidos: {movidos}")
    else:
        print("No se encontraron archivos sueltos para mover en la raíz de insumos/")

def main():
    parser = argparse.ArgumentParser(description="Gestor automático de proyectos y versiones para VideoFactory")
    parser.add_argument("--nombre", "-n", help="Nombre del video o versión (ej: 'video lunes parte 1')")
    parser.add_argument("--listar", "-l", action="store_true", help="Lista todos los proyectos existentes")
    parser.add_argument("--mover_sueltos", "-m", action="store_true", help="Mueve archivos sueltos de insumos/ al nuevo proyecto")
    args = parser.parse_args()

    if args.listar:
        listar_proyectos()
        return

    if not args.nombre:
        print("Error: Debes proporcionar --nombre '<nombre de tu video>' o usar --listar.")
        return

    slug = slugify(args.nombre)
    rutas = asegurar_carpetas_proyecto(slug)
    plan_creado = crear_plantilla_plan(rutas["insumos"], args.nombre, slug)

    print(f"\n PROYECTO INICIALIZADO:")
    print(f"  Nombre original : {args.nombre}")
    print(f"  Slug de sistema : {slug}")
    print(f"  Carpeta insumos : {rutas['insumos']}/")
    print(f"  Carpeta salida  : {rutas['salida']}/")
    print(f"  Carpeta public  : {rutas['public']}/")
    if plan_creado:
        print(f"  Plantilla creada: {rutas['insumos']}/plan.md")

    if args.mover_sueltos:
        print("\nReubicando archivos sueltos...")
        mover_archivos_sueltos(slug)

    print("\nListo. Coloca tus videos/audios en la carpeta de insumos sin preocuparte por sobreescribir otros proyectos.\n")

if __name__ == "__main__":
    main()
