import os
import shutil
from PIL import Image
from pathlib import Path
from tqdm import tqdm  # 用于显示进度条，如果没有安装可去掉 tqdm 相关代码

# ================= 配置区域 =================
# 源文件夹路径
SOURCE_FOLDER = r"C:\Users\han\Desktop\EastResearchAreas-336"

# 目标分辨率
TARGET_WIDTH = 342
TARGET_HEIGHT = 228

# 输出文件夹路径 (默认为源文件夹同名加 _resized，防止覆盖原图)
OUTPUT_FOLDER = r"C:\Users\han\Desktop\EastResearchAreas-342"

# 支持的图片格式
SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp')
# ===========================================

def resize_images():
    # 检查源文件夹是否存在
    if not os.path.exists(SOURCE_FOLDER):
        print(f"❌ 错误: 找不到源文件夹 '{SOURCE_FOLDER}'")
        return

    # 创建输出文件夹
    if os.path.exists(OUTPUT_FOLDER):
        print(f"⚠️ 输出文件夹已存在，将清空其中的内容: {OUTPUT_FOLDER}")
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    print(f"✅ 已创建输出文件夹: {OUTPUT_FOLDER}")
    print(f"🎯 目标分辨率: {TARGET_WIDTH} x {TARGET_HEIGHT}")
    print("-" * 50)

    # 获取所有图片文件
    files = [f for f in os.listdir(SOURCE_FOLDER) 
             if f.lower().endswith(SUPPORTED_FORMATS) and not f.startswith('.')]
    
    if not files:
        print("⚠️ 未在文件夹中找到任何图片文件。")
        return

    print(f"📂 找到 {len(files)} 张图片，开始处理...\n")

    success_count = 0
    error_count = 0

    # 使用 tqdm 显示进度条 (如果未安装 tqdm，直接用 for file in files: 即可)
    try:
        iterator = tqdm(files, desc="处理进度", unit="张")
    except NameError:
        # 如果没安装 tqdm，回退到普通列表
        iterator = files
        print("(提示: 安装 'tqdm' 库可显示漂亮的进度条: pip install tqdm)")

    for filename in iterator:
        src_path = os.path.join(SOURCE_FOLDER, filename)
        dst_path = os.path.join(OUTPUT_FOLDER, filename)

        try:
            with Image.open(src_path) as img:
                # 转换为 RGB 模式 (防止 PNG 透明通道等问题导致保存失败)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # 执行缩放 (RESIZE_LANCZOS 是高质量重采样滤波器)
                resized_img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
                
                # 保存
                # 根据扩展名决定保存质量，jpg 默认 95
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    resized_img.save(dst_path, quality=95, optimize=True)
                else:
                    resized_img.save(dst_path)
                
                success_count += 1

        except Exception as e:
            print(f"\n❌ 处理失败: {filename} - 错误信息: {e}")
            error_count += 1

    print("-" * 50)
    print(f"🎉 处理完成!")
    print(f"✅ 成功: {success_count} 张")
    if error_count > 0:
        print(f"❌ 失败: {error_count} 张")
    print(f"📁 结果已保存至: {OUTPUT_FOLDER}")

if __name__ == "__main__":
    # 尝试导入 tqdm，如果没有安装则忽略
    try:
        from tqdm import tqdm
    except ImportError:
        pass
    
    resize_images()
    
    # 暂停以便查看结果 (如果在命令行直接双击运行)
    input("\n按回车键退出...")