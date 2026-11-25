# Reglas Globales — Estudio de Video Automatizado (VideoFactory)

## 1. Arquitectura y Rutas del Proyecto
- **Directorio raíz:** `E:\Learning\NextGenAI\VideoFactory`
- **Entorno Python:** Usar siempre `.\.venv\Scripts\python.exe` (nunca el Python global) para ejecutar `faster-whisper`, `rembg` y `audio-offset-finder`.
- **Proyecto Remotion:** Vive en `./remotion/`. Todos los renders se ejecutan dentro de `./remotion/` usando `npx remotion render ...` y el output final se guarda en `../salida/`.
- **Assets temporales:** Cualquier archivo procesado listo para renderizar (`.webm` con alfa, `.mp3` sincronizado, `subtitulos.json`) debe copiarse a `./remotion/public/` antes de lanzar Remotion.

## 2. Identidad Visual y Formato Estándar
- **Resolución y FPS:** Siempre formato vertical `1080x1920` (9:16) a `30 fps`.
- **Estética:** Tecnológica, limpia y de ingeniería de software (fondo oscuro `#0B0F19`, acentos azul cian `#38BDF8` y esmeralda `#10B981`, tipografía `Inter` para títulos y `JetBrains Mono` para etiquetas técnicas).
- **Subtítulos:** Dinámicos en la zona media-baja (`bottom: 340px`, dejando libre la zona inferior donde TikTok/Reels ponen la descripción y botones), fuente grande en negrita con palabra activa resaltada en `#38BDF8`.
- **Identidad del creador:** Edson Moisés Silva Cárdenas — Enfoque en ingeniería de software, arquitectura, TDD y agentes de IA (evitar clichés de "hype" vacío).

## 3. Reglas de Ejecución y Consumo
- **Cero inspección multimedia directa:** Nunca intentar leer archivos `.mp4`, `.mp3` o `.webm` directamente en el contexto del LLM. Inspeccionar únicamente archivos `.md`, `.json`, `.tsx` y salidas de texto de CLI.
- **Limpieza:** No modificar los archivos base de `./remotion/src/` salvo que el `plan.md` pida crear o actualizar una escena específica.
- **Actualización obligatoria de funcionalidades.md:** Siempre que se cree o modifique una nueva skill, un nuevo agente, un script o cualquier funcionalidad técnica, se debe documentar y registrar de inmediato en `funcionalidades.md`.