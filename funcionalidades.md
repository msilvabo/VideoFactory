# Catálogo de Funcionalidades — VideoFactory

Guía completa de las capacidades, scripts, componentes de video y flujos automatizados de la factoría de video.

---

## Índice General de Funcionalidades

1. [Gestión Automática de Proyectos y Versiones](#1-gestión-automática-de-proyectos-y-versiones)
2. [Extracción y Filtrado Acústico de Audio contra Viento](#2-extracción-y-filtrado-acústico-de-audio-contra-viento)
3. [Corte Automático de Silencios, Pausas y Muletillas (_sinPausas)](#3-corte-automático-de-silencios-pausas-y-muletillas-_sinpausas)
4. [Transcripción Palabra por Palabra y Subtítulos con Whisper](#4-transcripción-palabra-por-palabra-y-subtítulos-con-whisper)
5. [Sincronización Automática Cámara-Micrófono por Forma de Onda](#5-sincronización-automática-cámara-micrófono-por-forma-de-onda)
6. [Generación de Voz Neuronal IA y Moduladores](#6-generación-de-voz-neuronal-ia-y-moduladores)
7. [Compositing Difuso Multicapa Detrás del Creador (BackdropInsert)](#7-compositing-difuso-multicapa-detrás-del-creador-backdropinsert)
8. [Zoom Dinámico Programático (Punch-In / Punch-Out)](#8-zoom-dinámico-programático-punch-in--punch-out)
9. [Subtítulos Dinámicos Cinéticos para TikTok / Reels](#9-subtítulos-dinámicos-cinéticos-para-tiktok--reels)
10. [Segmentación de Siluetas y Video con Canal Alfa (WebM VP9)](#10-segmentación-de-siluetas-y-video-con-canal-alfa-webm-vp9)
11. [Concatenación Automática de Escenas y Mezcla de Música](#11-concatenación-automática-de-escenas-y-mezcla-de-música)
12. [Inventario e Inspección Multimedia de Insumos](#12-inventario-e-inspección-multimedia-de-insumos)
13. [Sistema de Skills y Agentes de IA Autónomos](#13-sistema-de-skills-y-agentes-de-ia-autónomos)
14. [Reemplazo y Remuxing de Audio Mejorado en Video (Lossless Video)](#14-reemplazo-y-remuxing-de-audio-mejorado-en-video-lossless-video)
15. [Prerenderizado Rápido en Baja Calidad (Fast Preview)](#15-prerenderizado-rápido-en-baja-calidad-fast-preview)
16. [Generador de Animaciones Técnicas y Educativas Sincronizadas con Diálogo](#16-generador-de-animaciones-técnicas-y-educativas-sincronizadas-con-diálogo)
17. [Unión Inteligente de Escenas con Normalización Acústica y Transiciones Sutiles](#17-unión-inteligente-de-escenas-con-normalización-acústica-y-transiciones-sutiles)
18. [Suite de 9 Templates Verticales (9:16) de Alta Retención](#18-suite-de-9-templates-verticales-916-de-alta-retención)
19. [Extracción de Envolvente Acústica y Formas de Onda RMS](#19-extracción-de-envolvente-acústica-y-formas-de-onda-rms)

<br><br><br>
<br><br><br>

---
---

# Detalle Exhaustivo de cada Funcionalidad

---

### 1. Gestión Automática de Proyectos y Versiones

* **Archivo principal:** `scripts/gestor_proyecto.py`
* **Propósito:** Evitar borrar o sobreescribir archivos entre diferentes tomas, días o versiones de video. Permite que cada video viva en su propio entorno aislado y auto-contenido.
* **Qué hace:**
  * Recibe cualquier nombre en lenguaje natural (ej. `"video lunes parte 1"` o `"2026-11-23 falta de contexto"`).
  * Convierte el texto en un slug seguro para el sistema de archivos (`2026_11_23_falta_de_contexto`).
  * Crea de forma simultánea:
    * `insumos/<slug>/`: Para depositar videos crudos, audios y fotos. Incluye una plantilla automática `plan.md`.
    * `salida/<slug>/`: Destino de renders parciales y del video final normalizado.
    * `remotion/public/<slug>/`: Espacio de activos públicos que lee el motor de Remotion.
  * Muestra estadísticas globales de insumos y renders de todos los proyectos registrados.
* **Comandos de uso:**
  ```powershell
  # Crear un nuevo proyecto o toma
  .\.venv\Scripts\python.exe scripts/gestor_proyecto.py --nombre "video lunes parte 1"

  # Listar todos los proyectos existentes y su contenido
  .\.venv\Scripts\python.exe scripts/gestor_proyecto.py --listar

  # Mover archivos sueltos de la raíz de insumos/ hacia el nuevo proyecto
  .\.venv\Scripts\python.exe scripts/gestor_proyecto.py --nombre "video lunes parte 1" --mover_sueltos
  ```

---

### 2. Extracción y Filtrado Acústico de Audio contra Viento

* **Archivo principal:** `scripts/extraer_y_limpiar_audio.py`
* **Propósito:** Solucionar el problema de grabaciones con teléfono móvil en exteriores o terrazas donde el viento satura la cápsula del micrófono y dificulta la inteligibilidad.
* **Qué hace:**
  * **Modo Dual:** Procesa un video individual (`--video "toma.mp4"`) o escanea automáticamente todos los videos `.mp4`, `.mov`, `.mkv` de la carpeta del proyecto.
  * **Extracción de fidelidad:** Extrae la pista de audio sin compresión a WAV PCM 48kHz / 16-bit.
  * **Filtro contra viento de terraza:**
    * `highpass=f=115`: Corta el retumbo sordo y la presión de aire por debajo de 115 Hz sin quitar cuerpo a la voz.
    * `afftdn=nf=-24`: Reduce el soplido continuo y ruido ambiental estático.
    * `equalizer=f=3200`: Realce de inteligibilidad y brillo vocal (+3dB).
    * `compand`: Compresión dinámica que amortigua ráfagas repentinas de viento.
    * `loudnorm`: Normalización de sonoridad al estándar internacional de redes sociales (`-16 LUFS`, `TP -1.5`).
  * **Soporte de Estudio Externo (Adobe Podcast / ElevenLabs):** Si detecta en `insumos/<slug>/` un archivo con terminación `*_mejorado.wav`, `*_limpio.mp3` o `audio_estudio.wav`, lo prioriza automáticamente y lo enlaza directamente con Remotion sin aplicar filtros innecesarios.
* **Comandos de uso:**
  ```powershell
  # Extraer y filtrar todos los videos de un proyecto
  .\.venv\Scripts\python.exe scripts/extraer_y_limpiar_audio.py --proyecto "2026_11_23_falta_de_contexto"

  # Extraer y filtrar un video específico
  .\.venv\Scripts\python.exe scripts/extraer_y_limpiar_audio.py --proyecto "2026_11_23_falta_de_contexto" --video "toma_01.mp4"
  ```

---

### 3. Corte Automático de Silencios, Pausas y Muletillas (_sinPausas)

* **Archivo principal:** `scripts/recortar_silencios.py`
* **Propósito:** Eliminar tiempos muertos, dudas, respiraciones largas y **muletillas de relleno** (`eh`, `este`, `mmm`, `o sea`, `bueno`, etc.) en videos de cámara para acelerar el ritmo y maximizar la retención en TikTok, Reels y Shorts.
* **Qué hace:**
  * **Detección Dual:**
    1. Utiliza `pydub.silence.detect_nonsilent` para encontrar pausas mudas (`>350ms` a `-35 dBFS`).
    2. Utiliza `faster-whisper` para transcribir palabra por palabra e identificar fonemas de vacilación y muletillas del español (`eh`, `ehh`, `em`, `mmm`, `uh`, `ah`, `este`, `o sea`, etc.) con sus marcas exactas de tiempo.
  * **Corte Quirúrgico y Margen de Sílabas:** Resta los tramos de muletillas de la señal hablada aplicando un margen de protección (`50ms`) para no cortar consonantes válidas.
  * **Nomenclatura Automática:** Genera el video resultante con el sufijo `<nombre>_sinPausas.mp4` (ej. `inicio1_limpio_sinPausas.mp4`).
  * Opcionalmente permite añadir palabras personalizadas con `--muletillas "palabra1,palabra2"` o generar solo el archivo `tramos.json` con los timestamps.
* **Comandos de uso:**
  ```powershell
  # Cortar silencios y muletillas generando <nombre>_sinPausas.mp4 automáticamente
  .\.venv\Scripts\python.exe scripts/recortar_silencios.py --video "insumos/2026_11_23_falta_de_contexto/inicio1_limpio.mp4"

  # Añadir palabras de relleno personalizadas
  .\.venv\Scripts\python.exe scripts/recortar_silencios.py --video "insumos/toma.mp4" --muletillas "básicamente,digamos"

  # Solo cortar silencios mudos sin analizar muletillas
  .\.venv\Scripts\python.exe scripts/recortar_silencios.py --video "insumos/toma.mp4" --solo_silencios
  ```

---

### 4. Transcripción Palabra por Palabra y Subtítulos con Whisper

* **Archivo principal:** `scripts/procesar_audio.py`
* **Propósito:** Generar subtítulos sincronizados al milisegundo palabra por palabra para alimentar las animaciones cinéticas de Remotion.
* **Qué hace:**
  * Utiliza `faster-whisper` en CPU (`compute_type="int8"`, modelo `small` o `medium`).
  * Extrae cada palabra con su timestamp exacto (`start` y `end` en segundos con 3 decimales).
  * Exporta el resultado a `remotion/public/<proyecto>/subtitulos.json`.
  * Si se proporciona video y audio externo separados, ejecuta previamente la sincronización por claqueta.
* **Comandos de uso:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/procesar_audio.py --proyecto "2026_11_23_falta_de_contexto" --audio "insumos/2026_11_23_falta_de_contexto/audio_final.wav"
  ```

---

### 5. Sincronización Automática Cámara-Micrófono por Forma de Onda

* **Archivo principal:** Integrado en `scripts/procesar_audio.py` con `audio-offset-finder`
* **Propósito:** Permitir grabar el video con el teléfono y el audio con un micrófono externo (corbatero, condensador o grabadora), alineándolos automáticamente mediante una claqueta o aplauso.
* **Qué hace:**
  * Compara la forma de onda del audio del video de la cámara con el audio limpio del micrófono externo mediante cross-correlación espectral.
  * Encuentra el offset exacto en segundos (positivo o negativo).
  * Ejecuta FFmpeg con `-ss` para cortar el desfase y une el video de la cámara con el audio limpio en `video_sync.mp4`.
* **Comandos de uso:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/procesar_audio.py --proyecto "mi_proyecto" --video "insumos/camara.mp4" --audio "insumos/microfono.wav"
  ```

---

### 6. Generación de Voz Neuronal IA y Moduladores

* **Archivo principal:** `scripts/generar_voz.py`
* **Propósito:** Crear locuciones sintéticas gratuitas y de alta calidad para doblaje, personajes o mensajes automáticos.
* **Qué hace:**
  * Conexión asíncrona con `edge-tts` (voces neuronales en español como `es-MX-JorgeNeural`, `es-ES-AlvaroNeural`, `es-BO-MarceloNeural`).
  * Permite configurar velocidad (`rate`) y tono (`pitch`).
  * **Moduladores de audio FFmpeg integrados:**
    * `--estilo robot`: Vibración cibernética con trémolo a 45Hz, resonancia metálica y realce a 2.5 kHz.
    * `--estilo doom`: Tono grave imponente con `asetrate` y ecualización de graves profundos a 140 Hz.
* **Comandos de uso:**
  ```powershell
  # Voz neutra estándar
  .\.venv\Scripts\python.exe scripts/generar_voz.py --texto "Hola, bienvenidos a esta entrega técnica." --voz neutral --out "insumos/locucion.mp3"

  # Voz de robot con modulación cibernética
  .\.venv\Scripts\python.exe scripts/generar_voz.py --texto "Advertencia del sistema." --estilo robot --voz grave --out "remotion/public/audio_robot.mp3"
  ```

---

### 7. Compositing Difuso Multicapa Detrás del Creador (BackdropInsert)

* **Archivo principal:** `remotion/src/BackdropInsert.tsx`
* **Propósito:** Proyectar imágenes, contratos, ventanas de código, interfaces o videos **detrás del presentador**, pero **por delante de la pared/fondo real**, fundiéndose con un desvanecimiento suave.
* **Qué hace:**
  * **Modos de posición:**
    * `'lateral-left'` y `'lateral-right'`: Ocupa el 50-60% lateral de la pantalla y se desvanece hacia el centro detrás del cuerpo del presentador.
    * `'vertical-top'` y `'vertical-bottom'`: Se ubica en el tercio superior o inferior detrás de los hombros o el escritorio.
  * **Máscaras de gradiente:** Implementa `mask-image: linear-gradient(...)` con porcentaje de difuminado (`featherPercent`) y desenfoque (`blur`).
  * **Cabecera Tech:** Barra de ventana con botones de control estilo macOS y etiquetas tipográficas técnicas en `JetBrains Mono`.
  * **Física de entrada:** Animación fluida con `spring` (amortiguación suave) y salida con disolución.
* **Ejemplo de integración en Remotion:**
  ```tsx
  <BackdropInsert
    src="captura_contrato.png"
    type="image"
    mode="lateral-left"
    startFrame={30}
    durationFrames={120}
    featherPercent={35}
    title="CONTRATO / REVISIÓN"
    subtitle="Cláusula de Arquitectura v2"
  />
  ```

---

### 8. Zoom Dinámico Programático (Punch-In / Punch-Out)

* **Archivos principales:** `remotion/src/DynamicZoom.tsx`, `remotion/src/ZoomVideoComposite.tsx` y `scripts/aplicar_zoom_dinamico.py`
* **Propósito:** Emular la edición de video moderna donde la cámara hace acercamientos enfáticos (*punch-in*) en frases clave y vuelve a plano general (*punch-out*), maximizando la atención en TikTok.
* **Qué hace:**
  * Envoltorio React que toma cualquier grupo de capas (fondo, gráficos y persona).
  * Recibe una lista de `zoomPoints` con fotograma de inicio (`startFrame`), escala objetivo (`scale: 1.12`) y punto de pivote en el rostro (`originY: '35%'`).
  * Suaviza la transición entre escalas mediante la física de resortes `spring` de Remotion.
* **Comando de uso automático:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/aplicar_zoom_dinamico.py --video insumos/<proyecto>/video_limpio_sinPausas.mp4 --scale 1.0
  ```

---

### 9. Subtítulos Dinámicos Cinéticos para TikTok / Reels

* **Archivos principales:** `remotion/src/SubtitulosWhisper.tsx` y `remotion/src/DoomsSubtitulos.tsx`
* **Propósito:** Mostrar subtítulos de lectura rápida en formato vertical optimizados para móvil.
* **Qué hace:**
  * Agrupación en bloques naturales de 3 o 4 palabras (*chunking*) para no saturar la pantalla.
  * **Palabra activa resaltada:** La palabra que el locutor está pronunciando se agranda (`scale(1.08)`) y cambia a color azul cian `#38BDF8` o verde `#10B981`.
  * **Zona segura garantizada (`bottom: 340px`):** Coloca el texto por encima de la descripción, botones de me gusta y comentarios de TikTok, Instagram Reels y YouTube Shorts.
  * Tipografía en `Inter` extra bold con sombras pronunciadas (`textShadow`) para lectura perfecta sobre cualquier fondo.

---

### 10. Segmentación de Siluetas y Video con Canal Alfa (WebM VP9)

* **Archivos principales:** `scripts/extraer_silueta_video.py`, `scripts/recortar_setup.py` y `scripts/extraer_silueta.py`
* **Propósito:** Aislar la persona u objetos del fondo para permitir composiciones tridimensionales en Remotion donde los textos y gráficos animados pasan por detrás del cuerpo.
* **Qué hace:**
  * Segmenta al presentador fotograma a fotograma utilizando `rembg` (red neuronal U2-Net / u2netp).
  * Codifica el video resultante en formato **WebM VP9 con canal alfa transparente (`yuva420p`, `alpha_mode: 1`)**, compatible de forma nativa con el motor de Remotion (`transparent={true}`).
  * Admite recorte puro de silueta (para exteriores o fondos dinámicos) y recorte con máscaras geométricas de escritorio/monitores.
* **Comando de uso:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/extraer_silueta_video.py --video insumos/<proyecto>/video.mp4 --out remotion/public/<proyecto>/silueta.webm
  ```

---

### 11. Concatenación Automática de Escenas y Mezcla de Música

* **Archivo principal:** `scripts/unir_escenas.py`
* **Propósito:** Unir múltiples escenas renderizadas por separado (`escena-01.mp4`, `escena-02.mp4`) en un video final continuo y añadir música de fondo.
* **Qué hace:**
  * Lee todas las escenas ordenadas dentro de `salida/<proyecto>/`.
  * Genera una lista de concatenación para FFmpeg con normalización a 30 fps y audio AAC a 192k.
  * Si existe `musica_fondo.mp3` en `insumos/<proyecto>/`, la mezcla automáticamente en bucle infinito atenuando su volumen al nivel deseado (por defecto `0.14`).
* **Comandos de uso:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/unir_escenas.py --proyecto "mi_proyecto" --volumen_musica 0.12
  ```

---

### 12. Inventario e Inspección Multimedia de Insumos

* **Archivo principal:** `scripts/inventario_insumos.py`
* **Propósito:** Analizar los archivos brutos de una carpeta de proyecto y devolver un reporte técnico en formato JSON estructurado.
* **Qué hace:**
  * Utiliza `ffprobe` y `Pillow` sin decodificar videos en el contexto del LLM.
  * Informa resolución exacta (`1080x1920`, `1920x1080`), duración en segundos y presencia de pistas de audio para cada video, foto y audio de la carpeta.
* **Comandos de uso:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/inventario_insumos.py --proyecto "2026_11_23_falta_de_contexto"
  ```

---

### 13. Sistema de Skills y Agentes de IA Autónomos

* **Directorio:** `.agents/skills/` y `.agents/rules/AGENTS.md`
* **Propósito:** Guiar a agentes de inteligencia artificial (como Antigravity) para ejecutar tareas complejas de dirección, edición y renderizado de forma autónoma.
* **Skills integradas:**
  * `guion-maestro`: Diseña la escaleta y genera los guiones `escena-XX.md` por proyecto.
  * `crear-short`: Orquesta el pipeline completo de un short desde el plan hasta el render final.
  * `render-escena`: Renderiza escenas específicas y las une.
  * `remotion-*`: Skills especializadas en composición, interactividad, tipografía y mejores prácticas de Remotion.

---

### 14. Reemplazo y Remuxing de Audio Mejorado en Video (Lossless Video)

* **Archivo principal:** `scripts/reemplazar_audio_video.py`
* **Propósito:** Sustituir la pista de audio original con viento o ruidos de la cámara por el audio mejorado (filtrado local o procesado externamente en Adobe Podcast/ElevenLabs) sin recodificar el video, garantizando cero pérdida de calidad visual y velocidad instantánea.
* **Qué hace:**
  * **Stream Copy de Video (`-c:v copy`):** No recodifica la imagen; clona el flujo de video H.264/HEVC original tal cual fue grabado por el teléfono. Mantiene 100% la nitidez, tasa de cuadros y colores intactos, tardando menos de un segundo por archivo.
  * **Audio AAC de Máxima Fidelidad (`-c:a aac -b:a 320k`):** Inyecta el audio limpio o mejorado codificándolo a 320 kbps para máxima claridad y compatibilidad universal.
  * **Conservación de Originales:** Guarda el resultado como `<nombre>_limpio.mp4`, manteniendo el video original del teléfono a salvo.
  * **Modo Dual:**
    * Por lote (automático): Empareja cada `<nombre>.mp4` con su respectivo `<nombre>.mp3` o `<nombre>.wav` dentro del proyecto.
    * Individual: Permite especificar un video y audio concretos.
  * **Replicación automática:** Copia el video limpio a `remotion/public/<proyecto>/` para su uso inmediato en composiciones.
* **Comandos de uso:**
  ```powershell
  # Procesar en lote todos los videos del proyecto emparejando con sus audios
  .\.venv\Scripts\python.exe scripts/reemplazar_audio_video.py --proyecto "2026_11_23_falta_de_contexto"

  # Procesar un video específico con un audio específico
  .\.venv\Scripts\python.exe scripts/reemplazar_audio_video.py --proyecto "2026_11_23_falta_de_contexto" --video "inicio1.mp4" --audio "inicio1.mp3"
  ```

---

### 15. Prerenderizado Rápido en Baja Calidad (Fast Preview)

* **Archivo principal:** `scripts/prerender.py`
* **Propósito:** Generar una vista previa completa en video de Remotion en segundos (en lugar de varios minutos), para revisar ritmo, alineación de subtítulos, animaciones de entrada y mezclas de audio antes de lanzar el render pesado en 1080p.
* **Qué hace:**
  * **Resolución Ligera (540x960):** Aplica `--scale=0.5` para procesar 4 veces menos píxeles que en Full HD.
  * **Compresión Rápida:** Utiliza CRF alto (`--crf=28`) y codificación H.264 optimizada para velocidad.
  * **Guardado Automático:** Exporta directamente a `salida/<proyecto>/preview_<composicion>.mp4` con un peso menor a 2 MB.
* **Comandos de uso:**
  ```powershell
  # Prerenderizar la composición activa del proyecto
  .\.venv\Scripts\python.exe scripts/prerender.py --proyecto "2026_11_23_falta_de_contexto" --composicion "ShortRedesDemo"

  # Prerenderizar cualquier otra composición a escala personalizada
  .\.venv\Scripts\python.exe scripts/prerender.py --composicion "DoomsInicio" --scale 0.5
  ```

---

### 16. Generador de Animaciones Gráficas y Simbólicas Sincronizadas con Diálogo (Zero Text)

* **Archivos principales:** `scripts/generar_animacion_dialogo.py` y `remotion/src/TechAnimation.tsx`
* **Propósito:** Analizar el diálogo del video con Whisper y generar **animaciones puramente visuales, gráficas y simbólicas** (sin texto redundante para no saturar al espectador junto con los subtítulos), ilustrando la metáfora técnica con vectores en movimiento.
* **Qué hace:**
  * **Cero Texto Redundante:** Evita la sobrecarga cognitiva. El mensaje verbal se lee en los subtítulos de Whisper en la zona inferior; la animación en la zona alta ilustra la idea con metáforas gráficas puras.
  * **Metáforas Vectoriales SVG en Movimiento:**
    * **Chip Acelerado / IA:** Procesador con circuitos luminosos en `#38BDF8`, engranaje con rotación continua y rayo de velocidad (representa *"generar código a toda velocidad"*).
    * **Cable Desconectado con Chispas:** Bus de datos que intenta conectarse pero queda flotando roto con partículas oscilantes en `#F59E0B` (representa *"falta de contexto"*).
    * **Alerta Pulsante:** Triángulo de advertencia en `#EF4444` con ondas de choque concéntricas (representa *"ahí comienza tu problema"*).
  * **Estética:** Ventana flotante estilo cristal tech con desenfoque (`backdrop-filter: blur(20px)`), sombras profundas y luces de control estilo macOS.
  * **Sincronización:** Calcula el segundo exacto donde se pronuncian las palabras clave e inicia la animación fluida con `spring` de Remotion.
* **Comandos de uso:**
  ```powershell
  # Analizar diálogo y generar la escena gráfica simbólica correspondiente
  .\.venv\Scripts\python.exe scripts/generar_animacion_dialogo.py --video "insumos/2026_11_23_falta_de_contexto/inicio1_limpio_sinPausas.mp4"
  ```

---

### 17. Unión Inteligente de Escenas con Normalización Acústica y Transiciones Sutiles

* **Archivos principales:** `scripts/unir_videos_balanceados.py` y `remotion/src/UnirVideosComposition.tsx`
* **Propósito:** Unir múltiples clips de video en un orden específico definido por el usuario, eliminando de raíz las diferencias de volumen entre tomas y evitando los cortes secos o bruscos mediante transiciones visuales y sonoras sutiles.
* **Qué hace:**
  * **Normalización Acústica EBU R128 (-16.0 LUFS):** Procesa cada clip individualmente con compresión dinámica vocal y `loudnorm` calibrado a `-16 LUFS`, True Peak `-1.5 dBTP` y `LRA 9`. Garantiza que todas las escenas compartan exactamente la misma presencia y nivel de voz, sin que una se escuche más fuerte o débil que otra.
  * **Estandarización de Video Vertical (1080x1920 @ 30fps):** Homogeniza la resolución, escala y tasa de fotogramas de clips dispares (incluso si provienen de `720x1280` a 24 fps) sobre fondo oscuro `#0B0F19`, asegurando compatibilidad perfecta sin deformaciones.
  * **Transiciones Visuales Sutiles y Orgánicas:**
    * **`rebote` (Por defecto):** Micro-rebote elástico (*punch-bounce*) amortiguado de 6 a 8 fotogramas (~0.25s) que dinamiza la entrada del nuevo video sin ser invasivo.
    * **`zoom_suave`:** Acercamiento continuo fluido en el punto de cambio.
    * **`fade`:** Disolvencia cruzada limpia de 0.25s.
    * **`deslizamiento`:** Desplazamiento horizontal suave (*smooth push*).
    * **`corte`:** Unión directa sin solapamiento para edición clásica.
  * **Micro-Crossfade de Audio (40ms):** Transición triangular imperceptible entre pistas de audio contiguas que elimina por completo cualquier chasquido o pop digital en los cortes.
  * **Música de Fondo Opcional:** Mezcla inteligente de banda sonora atenuada bajo la voz con *ducking* automático.
* **Comandos de uso:**
  ```powershell
  # 1. Unir videos pasando el orden exacto por consola con efecto rebote y nivelación a -16 LUFS
  .\.venv\Scripts\python.exe scripts/unir_videos_balanceados.py --proyecto "2026_11_23_falta_de_contexto" --videos 1.mp4 2.mp4 3_1.mp4 --transicion rebote

  # 2. Unir usando un archivo de orden predefinido (orden.txt)
  .\.venv\Scripts\python.exe scripts/unir_videos_balanceados.py --proyecto "2026_11_23_falta_de_contexto" --orden orden.txt --transicion fade

  # 3. Unir con música de fondo atenuada automáticamente
  .\.venv\Scripts\python.exe scripts/unir_videos_balanceados.py --proyecto "2026_11_23_falta_de_contexto" --videos 1.mp4 2.mp4 3_1.mp4 --musica "insumos/musica.mp3" --volumen_musica 0.12
  ```

---

### 18. Suite de 9 Templates Verticales (9:16) de Alta Retención

* **Archivos principales:** `remotion/src/templates/` (`01_SplitKaraoke.tsx` a `09_SmartReframe.tsx`) y componentes en `remotion/src/components/`.
* **Propósito:** Ofrecer 9 layouts programáticos de nivel profesional optimizados para formato vertical (**1080x1920 a 30fps**) en TikTok, Instagram Reels y YouTube Shorts, maximizando la retención y el dinamismo visual.
* **Catálogo de Templates Disponibles:**
  1. **`Template01-SplitKaraoke`:** Pantalla dividida con imagen Ken Burns suave (55%), subtítulos karaoke palabra por palabra (15%) y cámara del presentador (30%).
  2. **`Template02-MagnifierFocus`:** Lupa magnificadora ($1.8\times$ - $2.5\times$) sobre zona de código o documento con fondo desenfocado y webcam en píldora/cápsula vertical.
  3. **`Template03-BentoGrid`:** Cuadrícula modular estilo Bento (1 tarjeta panorámica y 2 cuadradas) con animaciones escalonadas y video/subtítulos inferiores.
  4. **`Template04-BeforeAfter`:** Cortina comparativa Antes vs. Después con barrido de revelación vertical y línea divisoria luminosa.
  5. **`Template05-PresenterHUD`:** Presentador recortado con silueta transparente (WebM alfa VP9) sobre contenido a pantalla completa con subtítulos a la derecha.
  6. **`Template06-NewsCardWaveform`:** Tarjeta pop-up de noticia o cita con fondo oscurecido y visualizador dinámico de forma de onda acústica en tiempo real.
  7. **`Template07-VoxHighlighter`:** Estilo documental periodístico con recorte de artículo en ligera perspectiva 3D y subrayador animado en amarillo/neón guiando la lectura.
  8. **`Template08-KineticHook`:** Tipografía cinética gigante y explosiva con alternancia de pesos y colores sobre B-Roll oscuro, ideal para los primeros 3 segundos (*Hook*).
  9. **`Template09-SmartReframe`:** Adaptador inteligente de video horizontal `16:9` a vertical `9:16` con fondo blur inmersivo, paneo con auto-centrado, titular superior y barra de progreso.
* **Comandos de uso:**
  ```powershell
  # Previsualizar en vivo en el navegador (Remotion Studio)
  cd remotion; npm start

  # Renderizar cualquier template específico a MP4
  cd remotion
  npx remotion render Template01-SplitKaraoke ../salida/<proyecto>/split.mp4
  npx remotion render Template02-MagnifierFocus ../salida/<proyecto>/focus.mp4
  npx remotion render Template03-BentoGrid ../salida/<proyecto>/bento.mp4
  npx remotion render Template04-BeforeAfter ../salida/<proyecto>/comparativa.mp4
  npx remotion render Template05-PresenterHUD ../salida/<proyecto>/hud.mp4
  npx remotion render Template06-NewsCardWaveform ../salida/<proyecto>/noticia.mp4
  npx remotion render Template07-VoxHighlighter ../salida/<proyecto>/vox.mp4
  npx remotion render Template08-KineticHook ../salida/<proyecto>/hook.mp4
  npx remotion render Template09-SmartReframe ../salida/<proyecto>/reframe.mp4
  cd ..
  ```

---

### 19. Extracción de Envolvente Acústica y Formas de Onda RMS

* **Archivo principal:** `scripts/extraer_forma_onda.py`
* **Propósito:** Generar arreglos de amplitud normalizada (envolvente RMS) por fotograma (a 30 fps) para alimentar visualizadores de onda en tiempo real en Remotion (como en `Template06-NewsCardWaveform`).
* **Qué hace:**
  * Decodifica cualquier pista de audio o video con FFmpeg a PCM 16-bit 48kHz mono.
  * Calcula la raíz del valor cuadrático medio (RMS) por cada intervalo de fotograma.
  * Normaliza y suaviza los valores de 0.08 a 1.0, exportando a `remotion/public/<proyecto>/waveform.json`.
* **Comando de uso:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/extraer_forma_onda.py --audio "insumos/<proyecto>/audio_limpio.mp3" --proyecto "<proyecto>"
  ```





