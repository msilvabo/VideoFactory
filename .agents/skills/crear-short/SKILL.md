---
name: crear-short
description: Flujo directo para crear un short completo leyendo insumos/<proyecto>/plan.md y exportando a salida/<proyecto>/<proyecto>_final.mp4.
---

# Skill: Producción Directa de Short Multi-Proyecto (`crear-short`)

## Estructura Obligatoria por Proyecto
Recibe siempre el nombre del `<proyecto>` (ej. `code-cats`).
- **Insumos y `plan.md`:** `./insumos/<proyecto>/`
- **Archivos para Remotion:** `./remotion/public/<proyecto>/`
- **Video renderizado:** `./salida/<proyecto>/<proyecto>_final.mp4`

## Pasos de Ejecución
1. **Inicializar carpetas e inventario:**
   `.\.venv\Scripts\python.exe scripts/inventario_insumos.py --proyecto <proyecto>`
2. **Leer `./insumos/<proyecto>/plan.md`:**
   Identificar modo (`3-capas`, `pantalla`, `motion-ui`, `directo`), textos y archivos.
3. **Procesar Audio y Subtítulos dentro del proyecto:**
   `.\.venv\Scripts\python.exe scripts/procesar_audio.py --proyecto <proyecto> --audio "./insumos/<proyecto>/<audio>"`
4. **Copiar activos visuales a `./remotion/public/<proyecto>/`:**
   Cualquier foto o video usado por Remotion debe copiarse a `./remotion/public/<proyecto>/` y referenciarse como `"<proyecto>/<archivo>"`.
5. **Renderizar en `./salida/<proyecto>/`:**
   ```powershell
   cd remotion
   npx remotion render <Composicion> "../salida/<proyecto>/<proyecto>_final.mp4" --overwrite
   cd ..