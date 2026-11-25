---
name: robot-message
description: Genera un clip vertical con fondo transparente (.webm) de un robot hablando con voz robótica sincronizada y animación según el estado del mensaje para un juego.
---

# Skill: Generador de Mensajes de Robot (`robot-message`)

## Parámetros de Entrada
- **Texto (obligatorio):** La frase corta que dirá el robot.
- **Estado (opcional, por defecto `hablando`):**
  - `hablando` (Cian - informativo/normal)
  - `exito` (Verde - logro/misión cumplida)
  - `alerta` (Rojo - peligro/error con vibración)
  - `advertencia` (Ámbar - precaución)
- **Tamaño (opcional, por defecto `600x800`):** Si el usuario no especifica otro, usar `600x800` px. Si pide otro tamaño:
  - Compacto UI: `450x600`
  - Estándar Popup: `600x800`
  - Grande HD: `900x1200`
- **Voz (opcional):** Si el usuario no pide cambiarla, usar siempre la configuración actual de `scripts/generar_voz.py` (`--estilo robot --voz grave`).
- **Archivo de salida (opcional):** Por defecto `./salida/robot_<estado>.webm`.

## Flujo de Ejecución Paso a Paso

1. **Caché de Imagen Transparente (`robot_transparente.png`):**
   - Verifica si ya existe `./insumos/robot_transparente.png`.
   - **Si NO existe:** Toma `./insumos/robot.png` y recorta su fondo ejecutando:
     `.\.venv\Scripts\rembg.exe i insumos/robot.png insumos/robot_transparente.png`
   - **Si YA existe:** Reutiliza directamente `./insumos/robot_transparente.png` sin volver a ejecutar `rembg`.
   - Copia `./insumos/robot_transparente.png` a `./remotion/public/robot_transparente.png`.

2. **Generación de Voz Robótica y Timestamps:**
   - Genera la locución con la configuración actual:
     `.\.venv\Scripts\python.exe scripts/generar_voz.py --texto "<Texto>" --estilo robot --voz grave --out remotion/public/audio_robot.mp3`
   - Genera los timestamps palabra por palabra en `./remotion/public/subtitulos.json` para que el robot pulse al ritmo de su voz:
     `.\.venv\Scripts\python.exe scripts/procesar_audio.py --audio remotion/public/audio_robot.mp3`

3. **Ajuste de Duración Exacta:**
   - Mide la duración exacta en segundos de `remotion/public/audio_robot.mp3` con `ffprobe`:
     `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 remotion/public/audio_robot.mp3`
   - Calcula `frames = Math.ceil((duracion_segundos + 0.4) * 30)` y actualiza `durationInFrames` (y `width`/`height` si el usuario pidió otra dimensión) en la composición `RobotMessage` dentro de `./remotion/src/Root.tsx`.

4. **Render con Canal Alfa (Fondo Transparente `.webm`):**
   - Entra a `./remotion/` y ejecuta el render con soporte de transparencia VP9:
     `npx remotion render RobotMessage ../salida/<nombre_salida>.webm --image-format=png --pixel-format=yuva420p --codec=vp9 --props="{\"robotImg\":\"robot_transparente.png\",\"audioSrc\":\"audio_robot.mp3\",\"estado\":\"<estado>\"}"`
   - Informa al usuario la ruta del archivo `.webm` listo para incrustar sobre el juego.

## Articulación de Cabeza y Manos (Rigging 2D)
- El componente `RobotMessage.tsx` no cambia el tamaño del robot ni lo hace temblar; divide `robot_transparente.png` en 4 zonas articuladas (Cabeza, Torso fijo, Brazo Izquierdo y Brazo Derecho) que se mueven al ritmo de las palabras de `subtitulos.json`.
- **Ajuste de anatomía opcional en `--props`:**
  - `corteCuelloY` (por defecto `38`): Altura porcentual (0-100) donde está el cuello del robot. Si el robot es cabezón (estilo chibi), usar `45` o `50`.
  - `corteHombroIzqX` (por defecto `28`) y `corteHombroDerX` (por defecto `72`): Posición horizontal donde nacen los brazos/manos.   