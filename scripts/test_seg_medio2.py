from PIL import Image
import numpy as np
from rembg import new_session, remove

session = new_session("u2netp")
img = Image.open("C:/Users/silva/.gemini/antigravity-cli/brain/0c58665a-a810-4804-82de-96542eec7db0/test_medio2_frame.jpg")
out = remove(img, session=session)
out.save("C:/Users/silva/.gemini/antigravity-cli/brain/0c58665a-a810-4804-82de-96542eec7db0/test_medio2_seg.png")
alpha = np.array(out)[:, :, 3]
y_indices, x_indices = np.where(alpha > 50)
print(f"Segmentacion OK! Person bbox: top={y_indices.min()}, bottom={y_indices.max()}, left={x_indices.min()}, right={x_indices.max()}")
