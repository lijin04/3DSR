import os
from PIL import Image
import glob

# ================= 配置区域 =================
# 输入文件夹路径 (你的原始图片)
input_folder = r"C:\Users\han\Desktop\3DSR-main\data\colmap\images" 
# 输出文件夹路径 (处理后的图片)
output_folder = r"C:\Users\han\Desktop\3DSR-main\data\colmap\images"
# ===========================================

def make_16_multiple(size):
    w, h = size
    # 计算向下取整的 16 的倍数
    new_w = (w // 16) * 16
    new_h = (h // 16) * 16
    return new_w, new_h

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']
image_files = []
for ext in image_extensions:
    image_files.extend(glob.glob(os.path.join(input_folder, ext)))

print(f"找到 {len(image_files)} 张图片，开始处理...")

for img_path in image_files:
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            new_w, new_h = make_16_multiple((w, h))
            
            if new_w == w and new_h == h:
                print(f"跳过 (已是 16 倍数): {os.path.basename(img_path)} ({w}x{h})")
                # 即使尺寸合适，也复制一份到输出目录以防万一
                img.save(os.path.join(output_folder, os.path.basename(img_path)))
                continue
            
            # 居中裁剪 (Center Crop)
            left = (w - new_w) / 2
            top = (h - new_h) / 2
            right = (w + new_w) / 2
            bottom = (h + new_h) / 2
            
            img_cropped = img.crop((left, top, right, bottom))
            
            save_path = os.path.join(output_folder, os.path.basename(img_path))
            img_cropped.save(save_path)
            print(f"已处理: {os.path.basename(img_path)} | {w}x{h} -> {new_w}x{new_h}")
            
    except Exception as e:
        print(f"处理失败 {img_path}: {e}")

print("所有图片处理完成！请更新你的训练代码以指向新的输出文件夹。")