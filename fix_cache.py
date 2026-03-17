import os
import shutil
import hashlib
from pathlib import Path

# ================= 配置区域 =================
# 1. 你下载好的文件完整路径 (请确认这里是否正确！)
YOUR_DOWNLOADED_FILE = r"C:\Users\han\Downloads\open_clip_pytorch_model.bin" 

# 2. 模型信息 (不要改)
REPO_ID = "laion/CLIP-ViT-H-14-laion2B-s32B-b79K"
FILENAME = "open_clip_pytorch_model.bin"
# ===========================================

def fix_hf_cache():
    # 设置镜像环境变量
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    
    from huggingface_hub.constants import HF_HUB_CACHE
    from huggingface_hub.file_download import repo_folder_name
    
    print(f"🔍 正在检查文件: {YOUR_DOWNLOADED_FILE}")
    if not os.path.exists(YOUR_DOWNLOADED_FILE):
        print("❌ 错误：找不到你指定的文件！请检查路径是否正确。")
        return

    # 1. 获取目标仓库的缓存文件夹名称 (例如: models--laion--...)
    repo_cache_name = repo_folder_name(repo_id=REPO_ID, repo_type="model")
    
    # 2. 拼接完整路径
    full_cache_path = os.path.join(HF_HUB_CACHE, repo_cache_name)
    
    print(f"📂 目标缓存根目录: {full_cache_path}")

    # 3. 确保目录结构存在
    snapshots_dir = os.path.join(full_cache_path, "snapshots")
    refs_dir = os.path.join(full_cache_path, "refs")
    
    os.makedirs(snapshots_dir, exist_ok=True)
    os.makedirs(refs_dir, exist_ok=True)
    
    # 创建 main 引用文件 (防止某些版本检查失败)
    main_ref_file = os.path.join(refs_dir, "main")
    if not os.path.exists(main_ref_file):
        # 我们暂时写入一个假哈希，或者留空，通常不影响文件加载
        # 但为了严谨，我们稍后会根据实际创建的快照文件夹更新它
        pass

    # 4. 寻找或创建正确的 "Snapshots" 哈希文件夹
    commit_hash_folder = None
    
    # 查找现有的快照文件夹 (通常是一串哈希值)
    if os.path.exists(snapshots_dir):
        folders = [f for f in os.listdir(snapshots_dir) if os.path.isdir(os.path.join(snapshots_dir, f))]
        # 过滤掉以 "." 开头的隐藏文件夹
        folders = [f for f in folders if not f.startswith('.')]
        
        if folders:
            commit_hash_folder = folders[0] 
            print(f"✅ 发现现有快照文件夹: {commit_hash_folder}")
        else:
            # 如果没有，生成一个假的哈希文件夹名 (模拟 commit hash)
            # 使用模型ID的哈希作为伪 commit hash
            fake_hash = hashlib.sha256(REPO_ID.encode()).hexdigest()[:40]
            commit_hash_folder = fake_hash
            print(f"🆕 未找到快照文件夹，创建新的: {commit_hash_folder}")
            
    target_snapshot_dir = os.path.join(snapshots_dir, commit_hash_folder)
    os.makedirs(target_snapshot_dir, exist_ok=True)
    
    # 更新 refs/main 指向这个哈希文件夹
    with open(main_ref_file, "w") as f:
        f.write(commit_hash_folder)
    print(f"🔗 已更新 refs/main 指向: {commit_hash_folder}")

    # 5. 核心步骤：复制文件到快照目录
    target_file_path = os.path.join(target_snapshot_dir, FILENAME)
    
    print(f"📥 正在部署文件到: {target_file_path}")
    
    # 如果目标文件已存在，先删除（避免权限问题或旧文件干扰）
    if os.path.exists(target_file_path):
        try:
            os.remove(target_file_path)
            print("🗑️ 已删除旧的冲突文件")
        except PermissionError:
            print("⚠️ 无法删除旧文件，请确保没有其他程序占用它。")
            return
        
    try:
        shutil.copy(YOUR_DOWNLOADED_FILE, target_file_path)
        print("✅ 文件复制成功")
    except Exception as e:
        print(f"❌ 复制文件失败: {e}")
        return
    
    # 6. 验证大小
    original_size = os.path.getsize(YOUR_DOWNLOADED_FILE)
    new_size = os.path.getsize(target_file_path)
    
    if original_size == new_size:
        print("\n" + "="*50)
        print("🎉 成功！文件已正确部署到 Hugging Face 缓存。")
        print(f"   最终位置: {target_file_path}")
        print("   文件大小校验通过。")
        print("="*50)
        print("\n👉 现在请运行你的训练脚本:")
        print("   export HF_ENDPOINT=https://hf-mirror.com")
        print("   sh run_3dsr.sh")
    else:
        print("❌ 错误：文件复制后大小不一致，可能损坏。")
        print(f"   原大小: {original_size}, 新大小: {new_size}")

if __name__ == "__main__":
    fix_hf_cache()