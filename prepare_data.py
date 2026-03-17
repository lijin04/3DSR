import os
import shutil
from PIL import Image
from pathlib import Path
import argparse

def resize_images(input_dir, output_dir, scale_factor):
    """
    读取 input_dir 中的所有图片，缩放后保存到 output_dir
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 创建输出目录
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 支持的图片格式
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    
    images = [f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions]
    
    if not images:
        print(f"❌ 在 {input_dir} 中未找到任何图片文件。")
        return

    print(f"🚀 开始处理 {len(images)} 张图片，缩放比例：{scale_factor}...")
    
    for img_file in images:
        try:
            with Image.open(img_file) as img:
                # 转换为 RGB (防止 PNG 有透明通道导致问题)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                w, h = img.size
                new_w = int(w * scale_factor)
                new_h = int(h * scale_factor)
                
                # 确保尺寸至少为 1x1
                new_w = max(1, new_w)
                new_h = max(1, new_h)
                
                resized_img = img.resize((new_w, new_h), Image.LANCZOS)
                
                save_path = output_path / img_file.name
                # 统一保存为 PNG 或保持原格式，这里建议统一 PNG 以符合 3DGS 习惯
                if save_path.suffix.lower() != '.png':
                    save_path = save_path.with_suffix('.png')
                    resized_img.save(save_path, format='PNG')
                else:
                    resized_img.save(save_path)
                    
        except Exception as e:
            print(f"⚠️ 处理 {img_file.name} 时出错: {e}")

    print(f"✅ 完成！图片已保存至: {output_dir}")

if __name__ == "__main__":
    base_data_dir = "C:/Users/han/Desktop/vggt_colmap/Teaching342"
    source_images = os.path.join(base_data_dir, "images")
    
    if not os.path.exists(source_images):
        print(f"❌ 错误：找不到源文件夹 {source_images}")
        exit(1)

    # 根据 run_3dsr.sh 中的逻辑：
    # HR_factor = 4
    # 第一步训练需要: -r $((HR_factor * 4)) => -r 16 => 对应 images_16
    # 第二步训练需要: --init-img .../images_$((HR_factor * 4)) => images_16 (作为输入参考图? 不，通常是作为GT或者输入)
    # 注意：脚本里有一行 --init-img ${dataset_path}/${scene}/images_$((HR_factor * 4))
    # 这意味着它需要 images_16 作为输入给扩散模型。
    # 同时，通常 3DGS 还需要 images_4 (即 HR_factor) 用于最终评估或中间步骤，虽然脚本里主要用了 images_16。
    # 为了保险，我们生成 images_4 和 images_16。
    
    scales = {
        # "images_2": 0.5, # 1/16 分辨率
        "images_4": 0.25   # 1/4 分辨率
    }

    for folder_name, scale in scales.items():
        out_dir = os.path.join(base_data_dir, folder_name)
        if os.path.exists(out_dir) and len(os.listdir(out_dir)) > 0:
            print(f"⏭️  跳过 {folder_name} (已存在且非空)")
            continue
        print(f"\n--- 生成 {folder_name} ---")
        resize_images(source_images, out_dir, scale)

    print("\n🎉 所有数据准备完毕！现在可以运行 sh run_3dsr.sh 了。")
    print("💡 提示：如果 COLMAP 稀疏重建文件 (sparse/0) 不存在，可能还需要运行 COLMAP，但通常 images 文件夹同级需要有 sparse 文件夹。")
    print("   请检查 data/colmap 下是否有 'sparse' 文件夹。如果没有，你需要先运行 COLMAP 进行稀疏重建。")