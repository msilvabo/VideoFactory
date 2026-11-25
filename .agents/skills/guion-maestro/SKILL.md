---
name: guion-maestro
description: Gestiona proyectos de video aislados por carpetas (insumos/<proyecto>, salida/<proyecto>, remotion/public/<proyecto>), analiza sus archivos y genera guion-maestro.md y escena-XX.md.
---

# Skill: Director de Guion Maestro Multi-Proyecto (`guion-maestro`)

## Regla de Aislamiento por Proyecto
Todo video se trabaja bajo un identificador `<proyecto>` en minúsculas y sin espacios (ej. `code-cats`, `devfest-promo`).
- **Insumos y Guiones:** `./insumos/<proyecto>/`
- **Activos procesados para Remotion:** `./remotion/public/<proyecto>/`
- **Videos renderizados:** `./salida/<proyecto>/`

## Flujo de Ejecución Paso a Paso

1. **Inicialización y Creación de Carpetas del Proyecto:**
   - Ejecuta siempre primero el inventario con el nombre del proyecto (esto crea automáticamente `insumos/<proyecto>`, `salida/<proyecto>` y `remotion/public/<proyecto>` si no existen):
     `.\.venv\Scripts\python.exe scripts/inventario_insumos.py --proyecto <proyecto>`
   - **Nota de migración:** Si el usuario acaba de crear el proyecto y dejó los archivos sueltos en la raíz de `./insumos/`, muévelos automáticamente a `./insumos/<proyecto>/` con `Move-Item` y vuelve a correr `inventario_insumos.py --proyecto <proyecto>`.

2. **Análisis de Audio y Tiempos:**
   - Si hay videos con voz o audios en `./insumos/<proyecto>/`, procésalos indicando el proyecto:
     `.\.venv\Scripts\python.exe scripts/procesar_audio.py --audio "./insumos/<proyecto>/<archivo>" --proyecto <proyecto>`
   - Lee `./remotion/public/<proyecto>/subtitulos.json` para obtener las frases exactas y sus segundos.

3. **Propuesta de Escaleta Visual:**
   - Presenta al usuario la tabla con:
     - Orden exacto de aparición de cada video y foto de `./insumos/<proyecto>/`.
     - Qué videos se aceleran (`1.25x`, `1.5x`, `2.0x`) para mantener el ritmo.
     - Sincronización con la locución y la música de fondo.

4. **Generación de Guiones Aislados en `./insumos/<proyecto>/`:**
   - Una vez aprobado el orden, genera:
     - `./insumos/<proyecto>/guion-maestro.md`
     - `./insumos/<proyecto>/escena-01.md`, `escena-02.md`, etc.
   - Todas las rutas dentro de los `.md` deben apuntar a `insumos/<proyecto>/...`, `remotion/public/<proyecto>/...` y exportar los renders parciales a `salida/<proyecto>/escena-XX.mp4` y el final a `salida/<proyecto>/<proyecto>_final.mp4`.