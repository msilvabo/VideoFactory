from rembg import remove
from PIL import Image
import numpy as np

entrada = "insumos/robot.png"
salida_insumos = "insumos/robot_transparente.png"
salida_public = "remotion/public/robot_transparente.png"

with open(entrada, "rb") as i:
    input_data = i.read()
    # Alpha matting erosiona el borde tipo sticker alrededor del personaje
    output_data = remove(
        input_data,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=20,
        alpha_matting_erode_size=12
    )

with open(salida_insumos, "wb") as o:
    o.write(output_data)

# Filtro adicional para volver transparentes los píxeles del halo celeste exterior
img = Image.open(salida_insumos).convert("RGBA")
data = np.array(img)
r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

# Detecta el tono celeste brillante del borde (R bajo, G alto, B muy alto) en zonas semitransparentes/borde
mask_halo_celeste = (r < 90) & (g > 150) & (b > 220) & (a < 250)
data[mask_halo_celeste, 3] = 0

img_limpia = Image.fromarray(data)
img_limpia.save(salida_insumos)
img_limpia.save(salida_public)
print("ROBOT_TRANSPARENTE_LIMPIO_OK")