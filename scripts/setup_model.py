import os
import sys
import ssl
import json
import argparse
import subprocess
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

MODELSCOPE_URL = "https://www.modelscope.cn/models/jinaai/jina-embeddings-v2-base-zh/resolve/master"
HF_MIRROR_URL = "https://hf-mirror.com/jinaai/jina-embeddings-v2-base-zh/resolve/main"
OFFICIAL_URL = "https://huggingface.co/jinaai/jina-embeddings-v2-base-zh/resolve/main"

FILES = [
    ("tokenizer.json", "tokenizer.json"),
    ("onnx/model_quantized.onnx", "onnx/model_quantized.onnx")
]

def get_smart_default_dir():
    """
    智能分配模型存储路径，坚决规避 C 盘空间占用：
    1. 若 skill_root 所在驱动器非 C 盘（如当前 E 盘知识库），直接使用 <skill_root>/models
    2. 若 skill_root 在 C 盘，优先探测本机空闲的其他盘符（D:, E:, F:）
    3. 极端情况下回退至 skill_root 本地便携目录
    """
    skill_root = Path(__file__).resolve().parent.parent
    root_drive = skill_root.drive.upper() if skill_root.drive else ""
    if root_drive and root_drive != "C:":
        return skill_root / "models" / "jina-embeddings-v2-base-zh"
        
    if os.name == 'nt':
        # 探测非 C 盘且空间充足的盘符
        for drive_letter in ["D:\\", "E:\\", "F:\\"]:
            p = Path(drive_letter)
            if p.exists():
                return p / ".cache" / "obsidian-knowledge-map" / "models" / "jina-embeddings-v2-base-zh"
                
    return skill_root / "models" / "jina-embeddings-v2-base-zh"

def download_file(url, dest_path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(".tmp")
    
    print(f"--> 正在下载: {dest_path.name} ...")
    
    # 1. 优先尝试 Python urllib (带 SSL 容错与浏览器 UA)
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response, open(temp_path, 'wb') as out_file:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            block_size = 1024 * 1024 # 1MB
            
            while True:
                chunk = response.read(block_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = min(100.0, (downloaded / total_size) * 100)
                    mb_down = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r    进度: {percent:.1f}% ({mb_down:.1f} MB / {mb_total:.1f} MB)")
                else:
                    mb_down = downloaded / (1024 * 1024)
                    sys.stdout.write(f"\r    已下载: {mb_down:.1f} MB")
                sys.stdout.flush()
                
        print()
        if temp_path.exists() and temp_path.stat().st_size > 1000:
            temp_path.replace(dest_path)
            return True
    except Exception as e:
        print(f"\n[!] urllib 下载遇到问题 ({e})，正在调用系统 curl 引擎重试...")
        if temp_path.exists():
            try: temp_path.unlink()
            except Exception: pass

    # 2. 备用尝试：系统级 curl.exe 引擎 (Windows 10/11 及 Unix 内置，对 SSL/重定向抗性最强)
    try:
        curl_bin = "curl.exe" if os.name == "nt" else "curl"
        curl_cmd = [curl_bin, "-k", "-L", "-A", "Mozilla/5.0", "--progress-bar", "-o", str(temp_path), url]
        res = subprocess.run(curl_cmd, capture_output=False)
        if res.returncode == 0 and temp_path.exists() and temp_path.stat().st_size > 1000:
            temp_path.replace(dest_path)
            print("[OK] 系统 curl 引擎拉取成功！")
            return True
    except Exception as curl_err:
        print(f"[!] curl 调用失败: {curl_err}")
        if temp_path.exists():
            try: temp_path.unlink()
            except Exception: pass

    return False

def setup_model(target_dir=None, mirror=True):
    skill_root = Path(__file__).resolve().parent.parent
    if target_dir:
        out_dir = Path(target_dir).resolve()
    else:
        out_dir = get_smart_default_dir()
        
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 智能多源源列表：国内优先阿里魔搭 ModelScope，其次 HF 镜像，最后官方源
    if mirror:
        sources = [
            ("ModelScope (阿里魔搭)", MODELSCOPE_URL),
            ("HF-Mirror (国内镜像)", HF_MIRROR_URL),
            ("Hugging Face (官方源)", OFFICIAL_URL),
        ]
    else:
        sources = [
            ("Hugging Face (官方源)", OFFICIAL_URL),
            ("ModelScope (阿里魔搭)", MODELSCOPE_URL),
            ("HF-Mirror (国内镜像)", HF_MIRROR_URL),
        ]
    
    print(f"=== Obsidian Knowledge Map 嵌入模型极速就绪机制 ===")
    print(f"目标安装路径: {out_dir}")
    print(f"首选镜像引擎: {sources[0][0]}\n")
    
    success_all = True
    for remote_rel, local_rel in FILES:
        target_file = out_dir / local_rel
        if target_file.exists() and target_file.stat().st_size > 1000:
            print(f"[OK] 已存在: {local_rel} (跳过下载)")
            continue
            
        file_success = False
        for src_name, base_url in sources:
            url = f"{base_url}/{remote_rel}"
            print(f"--> 尝试源 [{src_name}]: {url}")
            ok = download_file(url, target_file)
            if ok:
                file_success = True
                break
                
        if not file_success:
            success_all = False
            print(f"[x] 文件拉取失败: {remote_rel}")
            break
            
    if success_all:
        print("\n[OK] 模型配置成功！")
        cfg_path = skill_root / "config.json"
        cfg_data = {}
        if cfg_path.exists():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg_data = json.load(f)
            except Exception:
                pass
        cfg_data["model_path"] = str(out_dir)
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg_data, f, indent=2, ensure_ascii=False)
            print(f"[OK] 已将模型路径自动保存至本地 {cfg_path.name}")
        except Exception:
            pass
        return True
    else:
        print("\n[!] 模型下载未全部完成，请检查网络连接后重试。")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="自动下载并配置知识地图所需的轻量 ONNX 嵌入模型")
    parser.add_argument("--target-dir", help="自定义模型存放目录（默认自动定位非系统盘）")
    parser.add_argument("--official", action="store_true", help="使用 Hugging Face 官方源而非国内镜像")
    args = parser.parse_args()
    
    success = setup_model(args.target_dir, mirror=not args.official)
    sys.exit(0 if success else 1)
