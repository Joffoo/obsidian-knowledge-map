import os
import sys
import re
import yaml
import json
from pathlib import Path
import argparse

# 1. Console Encoding Safety: prevent Windows GBK console crashes on unicode symbols
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 2. Windows MSVC Runtime Resolution: prioritize modern C++ runtime over outdated System32 binaries
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    msvc_candidates = [
        r"C:\Program Files\Microsoft Office\root\Office16",
        r"C:\Program Files\Common Files\microsoft shared\ClickToRun",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Redist\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\Shared\14.0\VC",
    ]
    for d in msvc_candidates:
        if os.path.exists(os.path.join(d, "msvcp140.dll")):
            try:
                os.add_dll_directory(d)
                break
            except Exception:
                pass

# 3. CRITICAL: Load ONNX Runtime and Tokenizers BEFORE scipy/OpenBLAS to prevent Windows threading conflicts
try:
    import onnxruntime as ort
except ImportError:
    ort = None

try:
    import tokenizers
    from tokenizers import Tokenizer
except ImportError:
    tokenizers = None
    Tokenizer = None

# 4. Scientific & visualization libraries
import numpy as np

# Import Theme Design System
try:
    from themes import get_theme, THEMES
except ImportError:
    from .themes import get_theme, THEMES

def resolve_model_dir(explicit_path=None):
    """
    Resolve embedding model directory through a 5-tier fallback cascade:
    1. Explicit path passed via CLI/code (--model)
    2. Environment variable: KNOWLEDGE_MAP_MODEL_DIR or EMBEDDING_MODEL_DIR
    3. Local private config file: config.json in skill root directory
    4. Relative portable models directory: <skill_root>/models/jina-embeddings-v2-base-zh
    5. User cache directory: ~/.cache/obsidian-knowledge-map/models/jina-embeddings-v2-base-zh
    """
    skill_root = Path(__file__).resolve().parent.parent

    # 1. Explicit argument
    if explicit_path:
        p = Path(explicit_path)
        if p.exists():
            return p
        raise FileNotFoundError(f"指定的嵌入模型路径不存在: {explicit_path}")

    # 2. Environment variable
    env_path = os.environ.get("KNOWLEDGE_MAP_MODEL_DIR") or os.environ.get("EMBEDDING_MODEL_DIR")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    # 3. Local config.json (git-ignored private configuration)
    config_file = skill_root / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                configured_path = cfg.get("model_path")
                if configured_path:
                    p = Path(configured_path)
                    if p.exists():
                        return p
        except Exception:
            pass

    # 4. Skill local models/ directory (portable mode)
    local_model = skill_root / "models" / "jina-embeddings-v2-base-zh"
    if local_model.exists():
        return local_model

    # 5. JIT Auto-Download (Agent Autonomous Execution)
    print("\n[i] 未检测到本地嵌入模型，正在自动触发极速就绪机制...")
    try:
        from setup_model import setup_model, get_smart_default_dir
    except ImportError:
        try:
            from .setup_model import setup_model, get_smart_default_dir
        except ImportError:
            setup_model = None
            get_smart_default_dir = None
            
    if setup_model:
        ok = setup_model()
        if ok:
            # 优先从刚保存的 config.json 读取
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        configured_path = cfg.get("model_path")
                        if configured_path and Path(configured_path).exists():
                            return Path(configured_path)
                except Exception:
                    pass
            if local_model.exists():
                return local_model
            if get_smart_default_dir:
                smart_p = get_smart_default_dir()
                if smart_p.exists():
                    return smart_p

    return None

class MapGenerator:
    def __init__(self, vault_path, model_dir=None, output_dir=None, style='davinci'):
        self.vault_path = Path(vault_path) if vault_path else Path(".")
        self.model_dir = resolve_model_dir(model_dir)
        self.output_dir = Path(output_dir) if output_dir else Path(".")
        self.style = style
        os.makedirs(self.output_dir, exist_ok=True)
        self.theme = get_theme(style)
        self.tokenizer = None
        self.session = None

    def _init_session(self):
        if self.model_dir is None:
            raise FileNotFoundError(
                "未找到嵌入模型 (Embedding Model)！\n"
                "你可以通过以下任意方式指定或配置模型：\n"
                "  1. 命令行参数：--model <模型目录>\n"
                "  2. 环境变量：设置 KNOWLEDGE_MAP_MODEL_DIR=<模型目录>\n"
                "  3. 配置文件：在 Skill 根目录下创建 config.json，写入 {\"model_path\": \"<模型目录>\"}\n"
                "  4. 自动下载：运行 python scripts/setup_model.py 自动将模型拉取至本地"
            )
        from tokenizers import Tokenizer
        if self.tokenizer is None:
            tok_path = self.model_dir / "tokenizer.json"
            if not tok_path.exists():
                raise FileNotFoundError(f"在 {self.model_dir} 中未找到 tokenizer.json")
            self.tokenizer = Tokenizer.from_file(str(tok_path))
            self.tokenizer.enable_padding(direction='right', pad_id=1, pad_type_id=0, pad_token='<pad>')
            self.tokenizer.enable_truncation(max_length=1024)
        
        onnx_candidates = [
            self.model_dir / "onnx" / "model_quantized.onnx",
            self.model_dir / "model_quantized.onnx",
            self.model_dir / "onnx" / "model_int8.onnx",
            self.model_dir / "model_int8.onnx",
            self.model_dir / "onnx" / "model.onnx",
            self.model_dir / "model.onnx",
        ]
        onnx_file = next((p for p in onnx_candidates if p.exists()), None)
        if not onnx_file:
            raise FileNotFoundError(f"在 {self.model_dir} 中未找到 ONNX 模型文件 (model_quantized.onnx 或 model.onnx)")
        self.onnx_path = str(onnx_file)
        
        import onnxruntime as ort
        import gc
        if self.session is not None:
            del self.session
            gc.collect()
        options = ort.SessionOptions()
        options.enable_cpu_mem_arena = False # Memory safety for large vaults
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.intra_op_num_threads = 2
        self.session = ort.InferenceSession(self.onnx_path, options, providers=['CPUExecutionProvider'])

    def scan_notes(self):
        """Universal vault scanner: only skips system/attachment folders starting with '_'"""
        notes = []
        for root, dirs, files in os.walk(self.vault_path):
            # Skip hidden/attachment folders like _attachments or .obsidian
            dirs[:] = [d for d in dirs if not d.startswith(('_', '.'))]
            for file in files:
                if file.endswith('.md'):
                    path = Path(root) / file
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except: continue
                    
                    # Generic Frontmatter Parsing
                    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                    fm = {}
                    if fm_match:
                        try: fm = yaml.safe_load(fm_match.group(1)) or {}
                        except: fm = {}
                    body = content[fm_match.end():] if fm_match else content
                    
                    # Basic noise filter: skip very short notes
                    if len(body) < 100: continue
                    
                    notes.append({
                        'title': fm.get('title', path.stem),
                        'rel_path': str(path.relative_to(self.vault_path)),
                        'content': body[:2000], 
                        'folder': path.parent.name if path.parent != self.vault_path else "Root"
                    })
        return notes

    def encode(self, texts):
        if self.session is None:
            self._init_session()
        all_embs = []
        total = (len(texts) + 3) // 4
        for i in range(0, len(texts), 4):
            batch_idx = i // 4 + 1
            if batch_idx % 10 == 0 or batch_idx == 1 or batch_idx == total:
                print(f"  Progress: Batch {batch_idx}/{total}...")
            
            # Auto-recycling to prevent memory leaks on large vaults
            if batch_idx % 50 == 0:
                self._init_session()
                
            batch = texts[i:i+4]
            enc = self.tokenizer.encode_batch(batch)
            ids = np.array([e.ids for e in enc], dtype=np.int64)
            mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
            out = self.session.run(None, {"input_ids": ids, "attention_mask": mask})[0]
            
            # Mean Pooling & Normalization
            mask_exp = np.expand_dims(mask, -1).astype(float)
            emb = np.sum(out * mask_exp, 1) / np.maximum(mask_exp.sum(1), 1e-9)
            emb /= np.maximum(np.linalg.norm(emb, axis=1, keepdims=True), 1e-9)
            all_embs.append(emb)
        return np.vstack(all_embs)

    def reduce_dimension_2d(self, embs, num_notes):
        """
        Robust 2D manifold projection with multi-engine fallback:
        1. UMAP (topological manifold)
        2. t-SNE (sklearn, precompiled wheel, non-linear)
        3. PCA (sklearn, linear)
        4. Pure NumPy SVD (zero external dependency, 100% fail-safe)
        """
        # 1. Try UMAP
        try:
            import umap
            n_neighbors = int(np.clip(np.sqrt(num_notes) * 2, 15, 100))
            min_dist = 0.1 if num_notes < 500 else 0.05
            reducer = umap.UMAP(n_components=2, metric='cosine', n_neighbors=n_neighbors, min_dist=min_dist, random_state=42)
            coords = reducer.fit_transform(embs)
            print("[OK] 已使用 UMAP 拓扑流形引擎完成降维")
            return coords
        except Exception as e:
            print(f"[i] UMAP 不可用 ({e})，正在自动切换至备用降维引擎...")

        # 2. Try scikit-learn t-SNE
        if num_notes >= 4:
            try:
                from sklearn.manifold import TSNE
                perplexity = min(30, max(2, num_notes // 3))
                coords = TSNE(n_components=2, metric='cosine', perplexity=perplexity, random_state=42).fit_transform(embs)
                print("[OK] 已使用 t-SNE 引擎完成降维")
                return coords
            except Exception:
                pass

        # 3. Try scikit-learn PCA
        try:
            from sklearn.decomposition import PCA
            coords = PCA(n_components=2, random_state=42).fit_transform(embs)
            print("[OK] 已使用 PCA 引擎完成降维")
            return coords
        except Exception:
            pass

        # 4. Pure NumPy SVD fallback (guaranteed to work everywhere numpy exists!)
        embs_centered = embs - np.mean(embs, axis=0)
        u, s, vt = np.linalg.svd(embs_centered, full_matrices=False)
        coords = u[:, :2] * s[:2]
        print("[OK] 已使用内置 SVD 引擎完成降维")
        return coords

    def analyze_geography(self):
        from scipy.stats import gaussian_kde
        from scipy.ndimage import maximum_filter
        from scipy.spatial.distance import cdist

        emb_cache = self.output_dir / "embeddings.npy"
        coord_cache = self.output_dir / "coords.npy"
        notes = self.scan_notes()
        num_notes = len(notes)
        
        if emb_cache.exists():
            embs = np.load(emb_cache)
        else:
            embs = self.encode([n['content'] for n in notes])
            np.save(emb_cache, embs)
            
        if coord_cache.exists():
            coords = np.load(coord_cache)
        else:
            coords = self.reduce_dimension_2d(embs, num_notes)
            coords = (coords - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0))
            np.save(coord_cache, coords)
        
        # KDE Density estimation on extended organic domain (zero artificial rectangular bounding)
        grid_pad = 0.15
        grid_min, grid_max = -grid_pad, 1.0 + grid_pad
        kde = gaussian_kde(coords.T)
        X, Y = np.meshgrid(np.linspace(grid_min, grid_max, 320), np.linspace(grid_min, grid_max, 320))
        Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(320, 320)
        Z = (Z - Z.min()) / (Z.max() - Z.min())
        
        # Peak Detection
        data_max = maximum_filter(Z, size=15, mode='constant')
        mask = (Z == data_max) & (Z > 0.1)
        peak_pts = np.column_stack(np.where(mask))
        peaks = sorted([{'val': Z[r,c], 'x': X[r,c], 'y': Y[r,c]} for r, c in peak_pts], key=lambda x: x['val'], reverse=True)
        
        # Dynamic Peak Merging
        merge_dist = 0.12 if num_notes < 500 else 0.08
        max_p = 6 if num_notes < 1000 else 10
        merged = []
        for p in peaks:
            if not any(np.sqrt((p['x']-mp['x'])**2 + (p['y']-mp['y'])**2) < merge_dist for mp in merged):
                merged.append(p)
            if len(merged) >= max_p: break
        
        # Extract cluster neighbors for Agent to summarize
        peak_neighbor_titles = []
        for p in merged:
            dists = cdist(np.array([[p['x'], p['y']]]), coords).flatten()
            nearest = [notes[j]['title'] for j in np.argsort(dists)[:15]]
            peak_neighbor_titles.append(nearest)
            
        state = {
            'notes': notes, 
            'coords': coords.tolist(), 
            'Z': Z.tolist(), 
            'peaks': merged,
            'grid_bounds': [grid_min, grid_max]
        }
        with open(self.output_dir / "map_state.json", 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)
        return peak_neighbor_titles

    def render(self, themes):
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors

        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.output_dir / "map_state.json", 'r', encoding='utf-8') as f:
            state = json.load(f)
        Z = np.array(state['Z'])
        coords = np.array(state['coords'])
        grid_bounds = state.get('grid_bounds', [-0.15, 1.15])
        grid_min, grid_max = grid_bounds[0], grid_bounds[1]
        X, Y = np.meshgrid(np.linspace(grid_min, grid_max, Z.shape[1]), np.linspace(grid_min, grid_max, Z.shape[0]))
        
        theme = self.theme
        paper_color = theme['bg_color']
        ink_color = theme['ink_color']
        secondary_color = theme.get('secondary_color', ink_color)
        accent_color = theme.get('accent_color', ink_color)
        
        font_candidates = theme.get('font_family_plt', ['Microsoft YaHei', 'sans-serif'])
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun'] + font_candidates
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(14, 14), dpi=150)
        fig.patch.set_facecolor(paper_color)
        ax.set_facecolor(paper_color)
        
        # 1. Seamless colormap: smoothly blends into background paper color
        cmap_colors = theme.get('cmap_colors', [])
        if cmap_colors and cmap_colors[0].lower() != paper_color.lower():
            cmap_colors = [paper_color] + list(cmap_colors[1:])
        cmap = mcolors.LinearSegmentedColormap.from_list(self.style, cmap_colors)
        
        # 2. Contour levels starting from 0.015 so outer ripples seamlessly fade into the paper
        num_levels = theme.get('contour_levels', 22)
        levels = np.linspace(0.015, 1.0, num_levels)
        ax.contourf(X, Y, Z, levels=levels, cmap=cmap, alpha=theme.get('contour_alpha', 0.65), extend='max')
        ax.contour(X, Y, Z, levels=levels, colors=ink_color, 
                   linewidths=theme.get('contour_line_width', 0.45), 
                   alpha=theme.get('contour_line_alpha', 0.28))
        
        # Universal Categorical Coloring from Style Palette
        folders = [n['folder'] for n in state['notes']]
        unique_f = sorted(list(set(folders)))
        color_palette = theme.get('scatter_palette', plt.colormaps['tab20'].colors if hasattr(plt, 'colormaps') else plt.cm.get_cmap('tab20').colors)
        palette_len = len(color_palette)
        edge_color = theme.get('scatter_edge_color', 'none')
        
        for i, f in enumerate(unique_f):
            m = np.array([n == f for n in folders])
            if any(m):
                c = color_palette[i % palette_len]
                ax.scatter(coords[m, 0], coords[m, 1], s=20, 
                           c=[c], alpha=0.8, label=f, 
                           edgecolors='none')
        
        # Peak Annotations with Centripetal Smart Offset (Zero Edge Clipping)
        markers = theme.get('peak_markers', ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'])
        badge_type = theme.get('peak_badge_type', 'circle')
        
        for i, (p, t) in enumerate(zip(state['peaks'], themes)):
            marker = markers[i % len(markers)]
            px, py = p['x'], p['y']
            
            # Smart Centripetal Placement: avoid clipping at canvas edges
            # If peak is on the right half (px > 0.60), place label to the LEFT of the marker
            # If peak is on the left half (px <= 0.60), place label to the RIGHT of the marker
            is_right = px > 0.60
            ha_text = 'right' if is_right else 'left'
            dx_text = -0.035 if is_right else 0.035
            
            # Vertical safety: if peak is near top or bottom edge, shift inward
            if py > 0.82:
                va_text = 'top'
                dy_text = -0.015
            elif py < 0.18:
                va_text = 'bottom'
                dy_text = 0.015
            else:
                va_text = 'center'
                dy_text = 0.005
                
            lx = px + dx_text
            ly = py + dy_text
            
            if badge_type == 'stamp':
                ax.text(px, py, marker, ha='center', va='center', color=accent_color, fontweight='bold', fontsize=10,
                        bbox=dict(boxstyle='square,pad=0.25', facecolor=paper_color, edgecolor=accent_color, linewidth=1.2, alpha=0.9))
                ax.text(lx, ly, t, ha=ha_text, va=va_text, color=ink_color, fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor=paper_color, edgecolor=secondary_color, alpha=0.8, linewidth=0.6))
            elif badge_type == 'crosshair':
                ax.plot([px-0.018, px+0.018], [py, py], color=accent_color, linewidth=0.8, alpha=0.85)
                ax.plot([px, px], [py-0.018, py+0.018], color=accent_color, linewidth=0.8, alpha=0.85)
                ax.add_artist(plt.Circle((px, py), 0.016, color=accent_color, fill=False, linewidth=0.8, alpha=0.7))
                ax.text(lx, ly, f"[{marker}] {t}", ha=ha_text, va=va_text, color=ink_color, fontsize=9,
                        bbox=dict(boxstyle='square,pad=0.25', facecolor=paper_color, edgecolor=accent_color, alpha=0.85, linewidth=0.8))
            elif badge_type == 'star':
                ax.plot(px, py, marker='*', markersize=13, color=accent_color, markeredgecolor='white', markeredgewidth=0.4)
                ax.text(lx, ly, f"{marker} · {t}", ha=ha_text, va=va_text, color=ink_color, fontsize=9,
                        bbox=dict(boxstyle='round,pad=0.25', facecolor=paper_color, edgecolor=secondary_color, alpha=0.75, linewidth=0.6))
            elif badge_type == 'swiss_box':
                ax.text(px, py, marker, ha='center', va='center', color='white', fontweight='heavy', fontsize=9,
                        bbox=dict(boxstyle='square,pad=0.3', facecolor=accent_color, edgecolor='none', alpha=1.0))
                ax.text(lx, ly, t.upper(), ha=ha_text, va=va_text, color=ink_color, fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='square,pad=0.25', facecolor=paper_color, edgecolor=ink_color, linewidth=1.0, alpha=0.9))
            elif badge_type == 'zen_circle':
                ax.add_artist(plt.Circle((px, py), 0.018, color=ink_color, fill=False, linewidth=1.0, alpha=0.75))
                ax.text(px, py, marker, ha='center', va='center', color=ink_color, fontsize=9, fontweight='bold')
                ax.text(lx, ly, t, ha=ha_text, va=va_text, color=ink_color, fontsize=10,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=paper_color, edgecolor=secondary_color, alpha=0.75, linewidth=0.6))
            else:
                ax.add_artist(plt.Circle((px, py), 0.018, color=ink_color, fill=False, alpha=0.85, linewidth=1.0))
                ax.text(px, py, marker, ha='center', va='center', color=ink_color, fontweight='bold', fontsize=9)
                ax.text(lx, ly, t, ha=ha_text, va=va_text, color=ink_color, fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor=paper_color, edgecolor=secondary_color, alpha=0.85, linewidth=0.6))
        
        vault_name = self.vault_path.name if self.vault_path and self.vault_path.name else "VAULT"
        main_title = theme.get('brand_title_format', 'OBSIDIAN KNOWLEDGE MAP').format(vault_name=vault_name)
        subtitle = theme.get('brand_subtitle', '')
        
        # Mathematically Centered Title (using figure coordinates for exact 0.5 horizontal midpoint)
        fig.text(0.5, 0.972, main_title, ha='center', va='top', fontsize=22, color=ink_color, fontweight='bold')
        if subtitle:
            fig.text(0.5, 0.944, subtitle, ha='center', va='top', fontsize=11, color=ink_color, alpha=0.8)
        
        leg = ax.legend(loc='lower left', frameon=True, facecolor=paper_color, edgecolor=secondary_color, fontsize=8, ncol=2 if len(unique_f)>10 else 1)
        plt.setp(leg.get_texts(), color=ink_color)
        ax.axis('off')
        ax.set_xlim(grid_min, grid_max)
        ax.set_ylim(grid_min, grid_max)
        
        # Pure borderless full-bleed layout: completely free of any outer frames, boxes, or lines
        plt.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.93)
        
        plt.savefig(self.output_dir / "knowledge_map.png")
        plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=['analyze', 'render'], required=True)
    parser.add_argument("--vault", default=".")
    parser.add_argument("--model", default=None, help="Embedding model directory (optional, auto-detected from config.json or env)")
    parser.add_argument("--output", default=".")
    parser.add_argument("--style", default='davinci')
    parser.add_argument("--themes")
    args = parser.parse_args()
    
    gen = MapGenerator(args.vault, args.model, args.output, args.style)
    if args.mode == 'analyze':
        print(json.dumps(gen.analyze_geography(), ensure_ascii=False))
    elif args.mode == 'render':
        if args.themes:
            themes = json.loads(args.themes)
        else:
            with open(gen.output_dir / "themes.json", 'r', encoding='utf-8') as f:
                themes = json.load(f)
        gen.render(themes)
