import os
import glob
from rembg import new_session, remove
from PIL import Image

def process_frames(src_dir="temp_frames", out_dir="temp_sin_fondo", max_frames=90):
    os.makedirs(out_dir, exist_ok=True)
    session = new_session("u2netp")
    
    frame_files = sorted(glob.glob(os.path.join(src_dir, "*.png")))[:max_frames]
    total = len(frame_files)
    print(f"Iniciando procesamiento de siluetas para {total} fotogramas...")
    
    for idx, path in enumerate(frame_files, start=1):
        filename = os.path.basename(path)
        dest_path = os.path.join(out_dir, filename)
        
        with Image.open(path) as img:
            out_img = remove(img, session=session)
            out_img.save(dest_path)
            
        if idx % 10 == 0 or idx == total:
            print(f"Progreso siluetas: {idx}/{total} ({round(idx/total*100)}%)")
            
    print("Segmentacion de siluetas completada exitosamente.")

if __name__ == "__main__":
    process_frames()
