from PIL import Image
from rembg import remove
import io

# Cargar la imagen descargada del chat
img = Image.open("insumos/robot_rig.png").convert("RGBA")
w, h = img.size

# Coordenadas porcentuales exactas de los 4 cuadrantes (evitando los textos superiores y las líneas divisorias)
piezas = {
    "robot_cabeza.png":    (int(w * 0.02), int(h * 0.08), int(w * 0.48), int(h * 0.41)),
    "robot_torso.png":     (int(w * 0.52), int(h * 0.08), int(w * 0.98), int(h * 0.41)),
    "robot_brazo_izq.png": (int(w * 0.02), int(h * 0.48), int(w * 0.48), int(h * 0.73)),
    "robot_brazo_der.png": (int(w * 0.52), int(h * 0.48), int(w * 0.98), int(h * 0.73)),
}

for nombre, caja in piezas.items():
    recorte = img.crop(caja)
    buf = io.BytesIO()
    recorte.save(buf, format="PNG")
    
    # Quitar el fondo gris oscuro de cada pieza individual
    sin_fondo = remove(buf.getvalue())
    
    ruta_insumos = f"insumos/{nombre}"
    ruta_public = f"remotion/public/{nombre}"
    
    with open(ruta_insumos, "wb") as f:
        f.write(sin_fondo)
    with open(ruta_public, "wb") as f:
        f.write(sin_fondo)
        
    print(f"PIEZA_LISTA={ruta_public}")