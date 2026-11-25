# VideoFactory — Guía de Contexto para Agentes de IA

Este documento resume la arquitectura, flujo operativo y reglas clave de **VideoFactory** para agentes autónomos.

---

## 1. Propósito del Proyecto
**VideoFactory** es un estudio automatizado para producir videos verticales (Shorts, Reels, TikTok) enfocados en ingeniería de software, arquitectura y agentes de IA, combinando procesamiento de audio/video con scripts en Python y renderizado programático con **Remotion** (React).

---

## 2. Estructura del Workspace
- `insumos/<proyecto>/`: Archivos multimedia brutos (videos de cámara, tomas, audios) y `plan.md`.
- `salida/<proyecto>/`: Renders intermedios, escenas renderizadas y video final ensamblado.
- `remotion/`: Proyecto React/Remotion:
  - `src/`: Composiciones, layouts, animaciones técnicas y subtítulos cinéticos.
  - `public/<proyecto>/`: Activos sincronizados listos para ser consumidos durante el render.
- `scripts/`: Herramientas CLI modulares en Python (filtros acústicos, Whisper, remoción de silencios, etc.).
- `.agents/skills/`: Skills especializadas (`crear-short`, `render-escena`, `guion-maestro`, `robot-message`).

---

## 3. Reglas Críticas de Ejecución
1. **Entorno Python obligatorio:** Usar siempre `.\.venv\Scripts\python.exe` (nunca el Python global).
2. **Renderizado Remotion:** Ejecutar desde `./remotion/` usando:
   ```powershell
   cd remotion; npx remotion render <CompositionName> ../salida/<proyecto>/<nombre>.mp4
   ```
3. **Cero inspección de binarios multimedia:** El agente **nunca** debe abrir ni leer directamente archivos binarios (`.mp4`, `.mp3`, `.webm`, etc.). Usar scripts de transcripción, FFprobe o metadatos JSON/MD.
4. **Aislamiento por proyecto:** No mezclar insumos ni sobreescribir archivos entre proyectos; cada video opera bajo su slug en `insumos/<slug>`, `salida/<slug>` y `remotion/public/<slug>`.
5. **Estándar visual:**
   - Formato vertical: `1080x1920` (9:16) a `30 fps`.
   - Paleta: Fondo `#0B0F19`, acentos `#38BDF8` (cian) y `#10B981` (esmeralda).
   - Tipografías: `Inter` (títulos/narrativa), `JetBrains Mono` (código/técnico).
   - Subtítulos: `bottom: 340px` (dejando despejada la interfaz de TikTok/Reels).
6. **Mantenimiento del Catálogo de Funcionalidades:**
   - Cada vez que se cree o modifique una nueva skill, un nuevo agente, un script o cualquier capacidad en el sistema, es **obligatorio actualizar `funcionalidades.md`** manteniendo la documentación y comandos al día.

---

## 4. Pipeline Típico y Comandos Rápidos
```powershell
# 1. Crear o preparar proyecto
.\.venv\Scripts\python.exe scripts/gestor_proyecto.py --nombre "mi_nuevo_video"

# 2. Extraer y limpiar audio (viento, normalización LUFS)
.\.venv\Scripts\python.exe scripts/extraer_y_limpiar_audio.py --proyecto "<slug>"

# 3. Recortar silencios y muletillas
.\.venv\Scripts\python.exe scripts/recortar_silencios.py --proyecto "<slug>"

# 4. Renderizar escena o composición Remotion
cd remotion
npx remotion render <Composition> ../salida/<slug>/<nombre>.mp4
cd ..

# 5. Concatenar escenas y mezcla final
.\.venv\Scripts\python.exe scripts/unir_videos_balanceados.py --proyecto "<slug>"
```
