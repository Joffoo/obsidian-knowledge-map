import os
import sys
import json
import argparse
import urllib.request
from pathlib import Path

MIRROR_URL = "https://hf-mirror.com/jinaai/jina-embeddings-v2-base-zh/resolve/main"
OFFICIAL_URL = "https://huggingface.co/jinaai/jina-embeddings-v2-base-zh/resolve/main"

FILES = [
    ("tokenizer.json", "tokenizer.json"),
    ("onnx/model_quantized.onnx", "onnx/model_quantized.onnx")
]

def download_file(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(".tmp")
    
    print(f"--> 正在下载: {dest_path.name} ...")
    
    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100.0, (downloaded / total_size) * 100)
            mb_down = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\r    进度: {percent:.1f}% ({mb_down:.1f} MB / {mb_total:.1f} MB)")
            sys.stdout.flush()
        else:
            mb_down = downloaded / (1024 * 1024)
            sys.stdout.write(f"\r    已下载: {mb_down:.1f} MB")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, temp_path, reporthook=reporthook)
        print()
        if temp_path.exists():
            temp_path.replace(dest_path)
            return True
    except Exception as e:
        print(f"\n[!] 下载失败 ({url}): {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False

def setup_model(target_dir=None, mirror=True):
    skill_root = Path(__file__).resolve().parent.parent
    if target_dir:
        out_dir = Path(target_dir).resolve()
    else:
        out_dir = skill_root / "models" / "jina-embeddings-v2-base-zh"
        
    out_dir.mkdir(parents=True, exist_ok=True)
    base_url = MIRROR_URL if mirror else OFFICIAL_URL
    backup_url = OFFICIAL_URL if mirror else MIRROR_URL
    
    print(f"=== Obsidian Knowledge Map 嵌入模型自动配置 ===")
    print(f"目标安装路径: {out_dir}")
    print(f"首选镜像源: {base_url}\n")
    
    success_all = True
    for remote_rel, local_rel in FILES:
        target_file = out_dir / local_rel
        if target_file.exists() and target_file.stat().st_size > 1000:
            print(f"[✓] 已存在: {local_rel} (跳过下载)")
            continue
            
        url = f"{base_url}/{remote_rel}"
        ok = download_file(url, target_file)
        if not ok:
            print(f"--> 尝试备用源: {backup_url}/{remote_rel} ...")
            ok = download_file(f"{backup_url}/{remote_rel}", target_file)
            
        if not ok:
            success_all = False
            print(f"[x] 文件拉取失败: {remote_rel}")
            break
            
    if success_all:
        print("\n[✓] 模型配置成功！")
        # 写入或更新 config.json
        cfg_path = skill_root / "config.json"
        cfg_data = {}
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg_data = json.load(f)
            except Exception:
                pass
        cfg_data["model_path"] = str(out_dir)
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg_data, f, indent=2, ensure_ascii=False)
        print(f"[✓] 已将模型路径记录至本地 {cfg_path.name}")
    else:
        print("\n[!] 模型下载未全部完成，请检查网络连接后重试。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动下载并配置知识地图所需的轻量 ONNX 嵌入模型")
    parser.add_argument("--target-dir", help="自定义模型存放目录（如 D:/Models/jina-embeddings-v2-base-zh）")
    parser.add_argument("--official", action="store_true", help="使用 Hugging Face 官方源而非国内镜像")
    args = parser.parse_args()
    
    setup_model(args.target_dir, mirror=not args.official)
