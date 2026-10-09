import os
import re
import yaml
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
from scipy.stats import gaussian_kde
from scipy.ndimage import maximum_filter
from scipy.spatial.distance import cdist
import sys
import argparse

# Import Theme Design System
try:
    from themes import get_theme, THEMES
except ImportError:
    from .themes import get_theme, THEMES

class MapGenerator:
    def __init__(self, vault_path, model_dir, output_dir, style='davinci'):
        self.vault_path = Path(vault_path) if vault_path else Path(".")
        self.model_dir = Path(model_dir) if model_dir else None
        self.output_dir = Path(output_dir) if output_dir else Path(".")
        self.style = style
        os.makedirs(self.output_dir, exist_ok=True)
        self.theme = get_theme(style)
        self.tokenizer = None
        self.session = None

    def _init_session(self):
        if self.model_dir is None:
            raise ValueError("model_dir is required for encoding/analysis.")
        from tokenizers import Tokenizer
        if self.tokenizer is None:
            self.tokenizer = Tokenizer.from_file(str(self.model_dir / "tokenizer.json"))
            self.tokenizer.enable_padding(direction='right', pad_id=1, pad_type_id=0, pad_token='<pad>')
            self.tokenizer.enable_truncation(max_length=1024)
        
        self.onnx_path = str(self.model_dir / "onnx/model_quantized.onnx")
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
            
            # Auto-recycling to prevent memory leaks
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

    def analyze_geography(self):
        import umap
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
            # Adaptive UMAP Parameters
            n_neighbors = int(np.clip(np.sqrt(num_notes) * 2, 15, 100))
            min_dist = 0.1 if num_notes < 500 else 0.05
            reducer = umap.UMAP(n_components=2, metric='cosine', n_neighbors=n_neighbors, min_dist=min_dist, random_state=42)
            coords = reducer.fit_transform(embs)
            coords = (coords - coords.min(axis=0)) / (coords.max(axis=0) - coords.min(axis=0))
            np.save(coord_cache, coords)
        
        # KDE Density estimation
        kde = gaussian_kde(coords.T)
        X, Y = np.meshgrid(np.linspace(0, 1, 300), np.linspace(0, 1, 300))
        Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(300, 300)
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
            
        state = {'notes': notes, 'coords': coords.tolist(), 'Z': Z.tolist(), 'peaks': merged}
        with open(self.output_dir / "map_state.json", 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)
        return peak_neighbor_titles

    def render(self, themes):
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.output_dir / "map_state.json", 'r', encoding='utf-8') as f:
            state = json.load(f)
        Z = np.array(state['Z'])
        coords = np.array(state['coords'])
        X, Y = np.meshgrid(np.linspace(0, 1, 300), np.linspace(0, 1, 300))
        
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
        
        cmap = mcolors.LinearSegmentedColormap.from_list(self.style, theme['cmap_colors'])
        
        levels = theme.get('contour_levels', 20)
        ax.contourf(X, Y, Z, levels=levels, cmap=cmap, alpha=theme.get('contour_alpha', 0.6))
        ax.contour(X, Y, Z, levels=levels, colors=ink_color, 
                   linewidths=theme.get('contour_line_width', 0.5), 
                   alpha=theme.get('contour_line_alpha', 0.3))
        
        # Universal Categorical Coloring from Style Palette
        folders = [n['folder'] for n in state['notes']]
        unique_f = sorted(list(set(folders)))
        color_palette = theme.get('scatter_palette', plt.cm.get_cmap('tab20').colors)
        palette_len = len(color_palette)
        edge_color = theme.get('scatter_edge_color', 'none')
        
        for i, f in enumerate(unique_f):
            m = np.array([n == f for n in folders])
            if any(m):
                c = color_palette[i % palette_len]
                ax.scatter(coords[m, 0], coords[m, 1], s=22, 
                           c=[c], alpha=0.75, label=f, 
                           edgecolors=edge_color, linewidths=0.3)
        
        # Peak Annotations with Badge Style
        markers = theme.get('peak_markers', ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'])
        badge_type = theme.get('peak_badge_type', 'circle')
        
        for i, (p, t) in enumerate(zip(state['peaks'], themes)):
            marker = markers[i % len(markers)]
            px, py = p['x'], p['y']
            
            if badge_type == 'stamp':
                ax.text(px, py, marker, ha='center', va='center', color=accent_color, fontweight='bold', fontsize=10,
                        bbox=dict(boxstyle='square,pad=0.25', facecolor=paper_color, edgecolor=accent_color, linewidth=1.2, alpha=0.9))
                ax.text(px+0.035, py+0.01, t, color=ink_color, fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor=paper_color, edgecolor=secondary_color, alpha=0.8, linewidth=0.6))
            elif badge_type == 'crosshair':
                ax.plot([px-0.018, px+0.018], [py, py], color=accent_color, linewidth=0.8, alpha=0.85)
                ax.plot([px, px], [py-0.018, py+0.018], color=accent_color, linewidth=0.8, alpha=0.85)
                ax.add_artist(plt.Circle((px, py), 0.016, color=accent_color, fill=False, linewidth=0.8, alpha=0.7))
                ax.text(px+0.025, py+0.012, f"[{marker}] {t}", color=ink_color, fontsize=9, fontfamily='monospace',
                        bbox=dict(boxstyle='square,pad=0.25', facecolor=paper_color, edgecolor=accent_color, alpha=0.85, linewidth=0.8))
            elif badge_type == 'star':
                ax.plot(px, py, marker='*', markersize=13, color=accent_color, markeredgecolor='white', markeredgewidth=0.4)
                ax.text(px+0.03, py+0.01, f"{marker} · {t}", color=ink_color, fontsize=9,
                        bbox=dict(boxstyle='round,pad=0.25', facecolor=paper_color, edgecolor=secondary_color, alpha=0.75, linewidth=0.6))
            elif badge_type == 'swiss_box':
                ax.text(px, py, marker, ha='center', va='center', color='white', fontweight='heavy', fontsize=9,
                        bbox=dict(boxstyle='square,pad=0.3', facecolor=accent_color, edgecolor='none', alpha=1.0))
                ax.text(px+0.032, py+0.01, t.upper(), color=ink_color, fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='square,pad=0.25', facecolor=paper_color, edgecolor=ink_color, linewidth=1.0, alpha=0.9))
            elif badge_type == 'zen_circle':
                ax.add_artist(plt.Circle((px, py), 0.018, color=ink_color, fill=False, linewidth=1.0, alpha=0.75))
                ax.text(px, py, marker, ha='center', va='center', color=ink_color, fontsize=9, fontweight='bold')
                ax.text(px+0.032, py+0.01, t, color=ink_color, fontsize=10,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=paper_color, edgecolor=secondary_color, alpha=0.75, linewidth=0.6))
            else:
                ax.add_artist(plt.Circle((px, py), 0.02, color=ink_color, fill=False, alpha=0.8))
                ax.text(px, py, marker, ha='center', va='center', color=ink_color, fontweight='bold')
                ax.text(px+0.03, py+0.01, t, color=ink_color, fontsize=10, 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=paper_color, edgecolor=ink_color, alpha=0.6))
        
        vault_name = self.vault_path.name if self.vault_path and self.vault_path.name else "VAULT"
        main_title = theme.get('brand_title_format', 'OBSIDIAN KNOWLEDGE MAP').format(vault_name=vault_name)
        subtitle = theme.get('brand_subtitle', '')
        
        ax.set_title(f"{main_title}\n{subtitle}" if subtitle else main_title, 
                     fontsize=24, color=ink_color, pad=35, fontweight='bold')
        
        leg = ax.legend(loc='lower left', frameon=True, facecolor=paper_color, edgecolor=secondary_color, fontsize=8, ncol=2 if len(unique_f)>10 else 1)
        plt.setp(leg.get_texts(), color=ink_color)
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(self.output_dir / "knowledge_map.png")
        plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=['analyze', 'render'])
    parser.add_argument("--vault"); parser.add_argument("--model"); parser.add_argument("--output")
    parser.add_argument("--style", default='davinci'); parser.add_argument("--themes")
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
