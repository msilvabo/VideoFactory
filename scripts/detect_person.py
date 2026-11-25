from PIL import Image
import numpy as np
from rembg import new_session, remove

session = new_session("u2netp")
img = Image.open("remotion/public/2026_11_23_falta_de_contexto/frame_160.jpg")
out = remove(img, session=session)
alpha = np.array(out)[:, :, 3]
y_indices, x_indices = np.where(alpha > 50)
print(f"Bounding box person: top={y_indices.min()}, bottom={y_indices.max()}, left={x_indices.min()}, right={x_indices.max()}")
