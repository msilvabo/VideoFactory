---
name: render-escena
description: Renderiza escenas individuales (escena-XX.md) desde insumos/<proyecto>/ hacia salida/<proyecto>/escena-XX.mp4, y une todas las escenas en el video final del proyecto.
---

# Skill: Ejecutor Modular de Escenas (`render-escena`)

## Rutas de Trabajo por Proyecto
- **Lectura de planes e insumos:** `./insumos/<proyecto>/`
- **Activos públicos de Remotion:** `./remotion/public/<proyecto>/`
- **Salida de escenas y video final:** `./salida/<proyecto>/`

## Flujo de Ejecución Paso a Paso

1. **Lectura del Plan de Escena:**
   - Lee `./insumos/<proyecto>/escena-XX.md` (o todas las escenas si el usuario pide renderizar todo el proyecto).
   - Asegúrate de que existan las carpetas `./insumos/<proyecto>`, `./salida/<proyecto>` y `./remotion/public/<proyecto>`.

2. **Pre-procesamiento de Audio y Video de la Escena:**
   - **Importante (Nombres con espacios):** Envuelve SIEMPRE entre comillas dobles `"..."` cualquier ruta de archivo en comandos de consola.
   - **Si la escena usa voz TTS (`generar_voz.py`):**
     ```powershell
     .\.venv\Scripts\python.exe scripts/generar_voz.py --proyecto <proyecto> --texto "<Frase>" --estilo limpia --voz neutral --out "./remotion/public/<proyecto>/audio_escena_XX.mp3"
     ```
   - **Si la escena requiere transcripción/subtítulos (`procesar_audio.py`):**
     ```powershell
     .\.venv\Scripts\python.exe scripts/procesar_audio.py --proyecto <proyecto> --audio "./remotion/public/<proyecto>/audio_escena_XX.mp3" --out_subs "./remotion/public/<proyecto>/subs_escena_XX.json"
     ```
   - **Si la escena requiere acelerar un video (`1.5x`, `2.0x`) o reencuadrarlo a 9:16 (1080x1920, 30fps):**
     ```powershell
     ffmpeg -y -i "./insumos/<proyecto>/<video_origen>" -vf "setpts=PTS/1.5,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30" -an -c:v libx264 -preset fast "./remotion/public/<proyecto>/video_escena_XX.mp4"
     ```
   - **Copia de fotos a `remotion/public/<proyecto>/`:**
     Copia las fotos que use la escena desde `./insumos/<proyecto>/` hacia `./remotion/public/<proyecto>/` (normalizando nombres sin espacios si es posible, ej. `foto_1.jpg`).

3. **Renderizado de la Escena en Remotion:**
   - Ajusta las `props` o la composición correspondiente en Remotion apuntando siempre a las rutas con el prefijo `<proyecto>/...` (ej. `staticFile("<proyecto>/foto_1.jpg")`) y renderiza hacia `./salida/<proyecto>/escena-XX.mp4`:
     ```powershell
     cd remotion
     npx remotion render <Composicion> "../salida/<proyecto>/escena-XX.mp4" --props="../insumos/<proyecto>/props_escena_XX.json" --overwrite
     cd ..
     ```

4. **Unión Final de Todas las Escenas (`unir_escenas.py`):**
   - Cuando todas las escenas `escena-01.mp4`, `escena-02.mp4`, etc. estén listas en `./salida/<proyecto>/`, únelas y mezcla la música de fondo ejecutando:
     ```powershell
     .\.venv\Scripts\python.exe scripts/unir_escenas.py --proyecto <proyecto>
     ```
   - Reporta al usuario la ruta final: `./salida/<proyecto>/<proyecto>_final.mp4`.