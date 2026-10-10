import json
import numpy as np
import plotly.graph_objects as go
import os
import urllib.parse
from pathlib import Path

# Import Theme Design System
try:
    from themes import get_theme, THEMES
except ImportError:
    from .themes import get_theme, THEMES

def generate_immersive_html(output_dir, vault_name, themes, style='shanshui'):
    output_dir = Path(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    state_path = output_dir / "map_state.json"
    
    if not state_path.exists():
        print(f"Error: map_state.json not found in {output_dir}")
        return
        
    with open(state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    notes = state['notes']
    coords = np.array(state['coords'])
    Z = np.array(state['Z'])
    peaks = state['peaks']
    
    # Selected initial theme
    initial_style = style if style in THEMES else 'shanshui'
    theme = get_theme(initial_style)
    bg_color = theme['bg_color']
    ink_color = theme['ink_color']
    secondary_color = theme.get('secondary_color', ink_color)
    accent_color = theme.get('accent_color', ink_color)
    contour_colors = theme['plotly_colorscale']
    
    # Adaptive border & line colors
    is_dark = bg_color in ['#050505', '#040208', '#0A192F', '#111111']
    line_color = 'rgba(255, 255, 255, 0.08)' if is_dark else 'rgba(0, 0, 0, 0.08)'
    legend_bg = 'rgba(20, 20, 25, 0.7)' if is_dark else 'rgba(245, 245, 240, 0.85)'
    hover_bg = 'rgba(15, 15, 20, 0.95)' if is_dark else 'rgba(255, 255, 255, 0.95)'
    hover_text = '#FFFFFF' if is_dark else ink_color
    hover_border = accent_color if is_dark else secondary_color
    
    # 1. Base Figure
    fig = go.Figure()

    # 2. Immersive Terrain (45 layers) - Trace 0
    grid_bounds = state.get('grid_bounds', [-0.15, 1.15])
    grid_min, grid_max = grid_bounds[0], grid_bounds[1]
    x_range = np.linspace(grid_min, grid_max, Z.shape[1])
    y_range = np.linspace(grid_min, grid_max, Z.shape[0])
    fig.add_trace(go.Contour(
        z=Z, x=x_range, y=y_range,
        colorscale=contour_colors,
        showscale=False,
        contours=dict(coloring='heatmap', showlines=True),
        line=dict(width=0.4, color=line_color),
        ncontours=45,
        hoverinfo='skip'
    ))

    # 3. Dynamic Clusters using Style Specific Palette - Traces 1 .. N
    folders = [n['folder'] for n in notes]
    unique_f = sorted(list(set(folders)))
    color_palette = theme.get('scatter_palette', [
        '#38BDF8', '#818CF8', '#C084FC', '#F472B6', '#34D399', '#FACC15'
    ])
    palette_len = len(color_palette)
    edge_color = theme.get('scatter_edge_color', 'rgba(255,255,255,0.3)' if is_dark else 'rgba(0,0,0,0.15)')
    if edge_color == 'none':
        marker_line = dict(width=0)
    else:
        marker_line = dict(width=0.6, color=edge_color)
    
    for i, f in enumerate(unique_f):
        indices = [j for j, val in enumerate(folders) if val == f]
        if not indices: continue
        
        folder_notes = [notes[j] for j in indices]
        x = coords[indices, 0]
        y = coords[indices, 1]
        titles = [n['title'] for n in folder_notes]
        urls = [f"obsidian://open?vault={urllib.parse.quote(vault_name)}&file={urllib.parse.quote(n['rel_path'])}" for n in folder_notes]
        
        c = color_palette[i % palette_len]
        
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='markers',
            marker=dict(
                size=6.5, 
                color=c, 
                opacity=0.9,
                line=marker_line
            ),
            name=f,
            text=titles,
            customdata=urls,
            hovertemplate="<b>%{text}</b><br><span style='font-size:10px; color:#888;'>CLICK TO OPEN IN OBSIDIAN</span><extra></extra>"
        ))

    # 4. AI Peak Labels with theme-specific badge typography - Traces N+1 .. N+M
    markers = theme.get('peak_markers', ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'])
    badge_type = theme.get('peak_badge_type', 'circle')
    font_family_web = theme.get('font_family_web', "sans-serif")
    
    for i, (p, t) in enumerate(zip(peaks, themes)):
        marker = markers[i % len(markers)]
        
        if badge_type == 'stamp':
            label_html = f"<span class='stamp-box'>{marker}</span>&nbsp;<span style='color:{ink_color}; font-weight:600; letter-spacing:2px;'>{t}</span>"
        elif badge_type == 'crosshair':
            label_html = f"<span style='color:{accent_color}; font-family:monospace; border:1px solid {accent_color}; padding:1px 4px; font-size:10px;'>{marker}</span>&nbsp;<span style='color:{ink_color}; letter-spacing:1px;'>{t}</span>"
        elif badge_type == 'star':
            label_html = f"<span style='color:{accent_color}; text-shadow:0 0 8px {accent_color}; font-weight:bold;'>✦ {marker}</span>&nbsp;<span style='color:{ink_color}; letter-spacing:2px;'>{t}</span>"
        elif badge_type == 'swiss_box':
            label_html = f"<span style='background:{accent_color}; color:#fff; padding:1px 5px; font-weight:bold; font-size:10px; margin-right:4px;'>{marker}</span><span style='color:{ink_color}; font-weight:bold; letter-spacing:1px;'>{t.upper()}</span>"
        elif badge_type == 'zen_circle':
            label_html = f"<span style='border:1px solid {secondary_color}; border-radius:50%; padding:0 5px; color:{secondary_color}; font-size:10px;'>{marker}</span>&nbsp;<span style='color:{ink_color}; letter-spacing:2px;'>{t}</span>"
        else:
            label_html = f"<span style='color:{secondary_color}; letter-spacing:3px; font-weight:bold;'>[{marker}] {t.upper()}</span>"
            
        fig.add_trace(go.Scatter(
            x=[p['x']], y=[p['y']],
            mode='text',
            text=[f"<span style='font-family:{font_family_web};'>{label_html}</span>"],
            textposition="top center",
            hoverinfo='skip',
            showlegend=False
        ))

    # 5. Full Screen Layout
    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[grid_min, grid_max]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[grid_min, grid_max]),
        showlegend=True,
        legend=dict(
            font=dict(color=ink_color, size=10, family=font_family_web),
            bgcolor=legend_bg,
            bordercolor=line_color,
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=0.03,
            xanchor='center',
            x=0.5,
            itemsizing='constant'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        clickmode='event',
        dragmode=False,
        hoverlabel=dict(
            bgcolor=hover_bg, 
            bordercolor=hover_border,
            font=dict(color=hover_text, size=12, family=font_family_web)
        ),
        autosize=True
    )

    html_content = fig.to_html(
        include_plotlyjs='cdn', 
        full_html=False, 
        config={'displayModeBar': False, 'responsive': True}
    )
    
    brand_title = theme.get('brand_title_format', '{vault_name} CONTOUR').format(vault_name=vault_name.upper())
    brand_subtitle = theme.get('brand_subtitle', '')
    custom_css = theme.get('html_custom_css', '')
    
    # Prepare serializable themes config for runtime browser switching
    runtime_themes = {}
    for k, v in THEMES.items():
        runtime_themes[k] = {
            'id': v['id'],
            'name': v['name'],
            'bg_color': v['bg_color'],
            'ink_color': v['ink_color'],
            'secondary_color': v.get('secondary_color', v['ink_color']),
            'accent_color': v.get('accent_color', v['ink_color']),
            'plotly_colorscale': v['plotly_colorscale'],
            'scatter_palette': v['scatter_palette'],
            'scatter_edge_color': v.get('scatter_edge_color', 'none'),
            'font_family_web': v['font_family_web'],
            'peak_markers': v['peak_markers'],
            'peak_badge_type': v['peak_badge_type'],
            'brand_title_format': v['brand_title_format'],
            'brand_subtitle': v.get('brand_subtitle', ''),
            'html_custom_css': v.get('html_custom_css', '')
        }
        
    themes_json_str = json.dumps(runtime_themes, ensure_ascii=False)
    peaks_json_str = json.dumps(peaks, ensure_ascii=False)
    themes_labels_json_str = json.dumps(themes, ensure_ascii=False)
    
    # Options for style selector dropdown
    style_options_html = "".join([
        f'<option value="{k}" {"selected" if k == initial_style else ""}>{v["name"]}</option>'
        for k, v in THEMES.items()
    ])

    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{vault_name} | Knowledge Map</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@200;400;700&family=JetBrains+Mono:wght@300;500&family=Noto+Serif+SC:wght@300;600&family=Songti+SC&family=STSong&display=swap" rel="stylesheet">
        <style>
            body, html {{ 
                margin: 0; padding: 0; 
                width: 100vw; height: 100vh; 
                background-color: {bg_color}; 
                overflow: hidden; 
                position: relative;
                font-family: {font_family_web};
                transition: background-color 0.4s ease;
            }}
            #main-stage {{ width: 100vw; height: 100vh; display: block; }}
            .plotly-graph-div {{ width: 100vw !important; height: 100vh !important; }}
            
            /* Top Left Brand Area */
            #brand-container {{
                position: absolute; 
                top: 32px; left: 40px;
                pointer-events: none; 
                z-index: 100;
                display: flex;
                flex-direction: column;
                gap: 5px;
                transition: all 0.3s ease;
            }}
            #brand {{
                font-size: 16px;
                letter-spacing: 6px;
                color: {ink_color};
                font-weight: 600;
                transition: color 0.3s ease;
            }}
            #brand-sub {{
                font-size: 10px;
                letter-spacing: 3px;
                color: {secondary_color};
                opacity: 0.75;
                text-transform: uppercase;
                transition: color 0.3s ease;
            }}
            
            /* Top Right Style Switcher Capsule (huashu-design) */
            #style-switcher-capsule {{
                position: absolute;
                top: 28px; right: 36px;
                z-index: 1000;
                display: flex;
                align-items: center;
                gap: 8px;
                background: { "rgba(20, 20, 25, 0.7)" if is_dark else "rgba(255, 255, 255, 0.85)" };
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid { "rgba(255, 255, 255, 0.15)" if is_dark else "rgba(0, 0, 0, 0.1)" };
                border-radius: 30px;
                padding: 6px 14px 6px 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                transition: all 0.3s ease;
            }}
            #style-switcher-capsule:hover {{
                box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15);
                transform: translateY(-1px);
            }}
            .capsule-icon {{
                font-size: 14px;
                opacity: 0.7;
                user-select: none;
            }}
            #style-select {{
                appearance: none;
                -webkit-appearance: none;
                -moz-appearance: none;
                background: transparent;
                border: none;
                outline: none;
                color: { "#FFFFFF" if is_dark else ink_color };
                font-size: 12px;
                font-weight: 500;
                font-family: inherit;
                cursor: pointer;
                padding-right: 18px;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath fill='none' stroke='%23888888' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' d='M1 1l4 4 4-4'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 2px center;
                transition: color 0.3s ease;
            }}
            #style-select option {{
                background-color: #1A1A1A;
                color: #FFFFFF;
                font-size: 12px;
                padding: 8px;
            }}

            .stamp-box {{
                border: 1.5px solid {accent_color};
                color: {accent_color};
                padding: 1px 4px;
                font-weight: bold;
                border-radius: 2px;
                background: rgba(236, 231, 222, 0.85);
                font-size: 10px;
            }}
        </style>
        <style id="theme-custom-style">
            {custom_css}
        </style>
    </head>
    <body>
        <div id="brand-container">
            <div id="brand">{brand_title}</div>
            <div id="brand-sub">{brand_subtitle}</div>
        </div>

        <div id="style-switcher-capsule">
            <span class="capsule-icon">🧭</span>
            <select id="style-select" title="切换地貌视觉风格">
                {style_options_html}
            </select>
        </div>

        <div id="main-stage">{html_content}</div>

        <script>
            const VAULT_NAME = "{vault_name}";
            const INITIAL_STYLE = "{initial_style}";
            const THEMES_DATA = {themes_json_str};
            const PEAKS_DATA = {peaks_json_str};
            const THEMES_LABELS = {themes_labels_json_str};
            const UNIQUE_FOLDERS_COUNT = {len(unique_f)};

            function applyTheme(styleKey) {{
                const theme = THEMES_DATA[styleKey] || THEMES_DATA['shanshui'];
                const isDark = ['#050505', '#040208', '#0A192F', '#111111'].includes(theme.bg_color);

                // 1. Update body and typography
                document.body.style.backgroundColor = theme.bg_color;
                document.body.style.fontFamily = theme.font_family_web;

                // 2. Update brand typography
                const brand = document.getElementById('brand');
                const brandSub = document.getElementById('brand-sub');
                if (brand) {{
                    brand.textContent = theme.brand_title_format.replace('{{vault_name}}', VAULT_NAME.toUpperCase());
                    brand.style.color = theme.ink_color;
                    brand.style.fontFamily = theme.font_family_web;
                }}
                if (brandSub) {{
                    brandSub.textContent = theme.brand_subtitle || '';
                    brandSub.style.color = theme.secondary_color || theme.ink_color;
                }}

                // 3. Update style switcher capsule appearance
                const capsule = document.getElementById('style-switcher-capsule');
                const selectEl = document.getElementById('style-select');
                if (capsule && selectEl) {{
                    capsule.style.background = isDark ? 'rgba(20, 20, 25, 0.7)' : 'rgba(255, 255, 255, 0.85)';
                    capsule.style.borderColor = isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.1)';
                    selectEl.style.color = isDark ? '#FFFFFF' : theme.ink_color;
                }}

                // 4. Update dynamic custom CSS
                const customStyleEl = document.getElementById('theme-custom-style');
                if (customStyleEl) {{
                    customStyleEl.innerHTML = (theme.html_custom_css || '') + `
                        .stamp-box {{
                            border: 1.5px solid ${{theme.accent_color}};
                            color: ${{theme.accent_color}};
                            padding: 1px 4px;
                            font-weight: bold;
                            border-radius: 2px;
                            background: rgba(236, 231, 222, 0.85);
                            font-size: 10px;
                        }}
                    `;
                }}

                // 5. Update Plotly Layout and Traces
                const plotEl = document.getElementsByClassName('plotly-graph-div')[0];
                if (!plotEl) return;

                const lineColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)';
                const legendBg = isDark ? 'rgba(20, 20, 25, 0.7)' : 'rgba(245, 245, 240, 0.85)';
                const hoverBg = isDark ? 'rgba(15, 15, 20, 0.95)' : 'rgba(255, 255, 255, 0.95)';
                const hoverText = isDark ? '#FFFFFF' : theme.ink_color;
                const hoverBorder = isDark ? theme.accent_color : (theme.secondary_color || theme.ink_color);

                // Atomic in-memory updates
                // 1. Update Layout
                plotEl.layout.paper_bgcolor = theme.bg_color;
                plotEl.layout.plot_bgcolor = theme.bg_color;
                if (plotEl.layout.legend) {{
                    plotEl.layout.legend.bgcolor = legendBg;
                    plotEl.layout.legend.bordercolor = lineColor;
                    if (plotEl.layout.legend.font) {{
                        plotEl.layout.legend.font.color = theme.ink_color;
                        plotEl.layout.legend.font.family = theme.font_family_web;
                    }}
                }}
                if (plotEl.layout.hoverlabel) {{
                    plotEl.layout.hoverlabel.bgcolor = hoverBg;
                    plotEl.layout.hoverlabel.bordercolor = hoverBorder;
                    if (plotEl.layout.hoverlabel.font) {{
                        plotEl.layout.hoverlabel.font.color = hoverText;
                        plotEl.layout.hoverlabel.font.family = theme.font_family_web;
                    }}
                }}

                // 2. Update Trace 0 (Contour)
                if (plotEl.data[0]) {{
                    plotEl.data[0].colorscale = theme.plotly_colorscale;
                    plotEl.data[0].line = {{ width: 0.4, color: lineColor }};
                }}

                // 3. Update Traces 1 .. UNIQUE_FOLDERS_COUNT (Folder Scatters)
                const edgeColor = theme.scatter_edge_color || 'none';
                const markerLine = (edgeColor === 'none') ? {{ width: 0 }} : {{ width: 0.6, color: edgeColor }};
                
                for (let i = 0; i < UNIQUE_FOLDERS_COUNT; i++) {{
                    const traceIdx = 1 + i;
                    if (plotEl.data[traceIdx] && plotEl.data[traceIdx].marker) {{
                        const color = theme.scatter_palette[i % theme.scatter_palette.length];
                        plotEl.data[traceIdx].marker.color = color;
                        plotEl.data[traceIdx].marker.line = markerLine;
                    }}
                }}

                // 4. Update Peaks Annotations
                const markers = theme.peak_markers || ['I', 'II', 'III', 'IV', 'V'];
                const badgeType = theme.peak_badge_type || 'circle';
                const peakStartIdx = 1 + UNIQUE_FOLDERS_COUNT;

                for (let i = 0; i < PEAKS_DATA.length; i++) {{
                    const traceIdx = peakStartIdx + i;
                    if (plotEl.data[traceIdx]) {{
                        const marker = markers[i % markers.length];
                        const t = THEMES_LABELS[i] || `PEAK ${{i+1}}`;
                        let labelHtml = '';

                        if (badgeType === 'stamp') {{
                            labelHtml = `<span class='stamp-box'>${{marker}}</span>&nbsp;<span style='color:${{theme.ink_color}}; font-weight:600; letter-spacing:2px;'>${{t}}</span>`;
                        }} else if (badgeType === 'crosshair') {{
                            labelHtml = `<span style='color:${{theme.accent_color}}; font-family:monospace; border:1px solid ${{theme.accent_color}}; padding:1px 4px; font-size:10px;'>${{marker}}</span>&nbsp;<span style='color:${{theme.ink_color}}; letter-spacing:1px;'>${{t}}</span>`;
                        }} else if (badgeType === 'star') {{
                            labelHtml = `<span style='color:${{theme.accent_color}}; text-shadow:0 0 8px ${{theme.accent_color}}; font-weight:bold;'>✦ ${{marker}}</span>&nbsp;<span style='color:${{theme.ink_color}}; letter-spacing:2px;'>${{t}}</span>`;
                        }} else if (badgeType === 'swiss_box') {{
                            labelHtml = `<span style='background:${{theme.accent_color}}; color:#fff; padding:1px 5px; font-weight:bold; font-size:10px; margin-right:4px;'>${{marker}}</span><span style='color:${{theme.ink_color}}; font-weight:bold; letter-spacing:1px;'>${{t.toUpperCase()}}</span>`;
                        }} else if (badgeType === 'zen_circle') {{
                            labelHtml = `<span style='border:1px solid ${{theme.secondary_color}}; border-radius:50%; padding:0 5px; color:${{theme.secondary_color}}; font-size:10px;'>${{marker}}</span>&nbsp;<span style='color:${{theme.ink_color}}; letter-spacing:2px;'>${{t}}</span>`;
                        }} else {{
                            labelHtml = `<span style='color:${{theme.secondary_color}}; letter-spacing:3px; font-weight:bold;'>[${{marker}}] ${{t.toUpperCase()}}</span>`;
                        }}

                        const fullText = `<span style='font-family:${{theme.font_family_web}};'>${{labelHtml}}</span>`;
                        plotEl.data[traceIdx].text = [fullText];
                    }}
                }}

                // 5. Single atomic render transaction via Plotly.react (replaces 14+ sequential redraws)
                Plotly.react(plotEl, plotEl.data, plotEl.layout);

                // Persist user selection
                try {{
                    localStorage.setItem('obsidian_map_style', styleKey);
                }} catch(e) {{}}
            }}

            window.addEventListener('load', function() {{
                var plot = document.getElementsByClassName('plotly-graph-div')[0];
                if(plot) {{
                    plot.on('plotly_click', function(data){{
                        if(data.points[0].customdata){{
                            window.location.href = data.points[0].customdata;
                        }}
                    }});
                }}

                // Bind Style Selector Change Event
                var selectEl = document.getElementById('style-select');
                if(selectEl) {{
                    selectEl.addEventListener('change', function(e) {{
                        applyTheme(e.target.value);
                    }});
                }}

                // Auto-restore saved user preference from localStorage
                var savedStyle = null;
                try {{ savedStyle = localStorage.getItem('obsidian_map_style'); }} catch(e) {{}}
                if(savedStyle && THEMES_DATA[savedStyle] && savedStyle !== INITIAL_STYLE) {{
                    if(selectEl) selectEl.value = savedStyle;
                    applyTheme(savedStyle);
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    html_path = output_dir / "knowledge_map.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Interactive HTML with live style switcher saved to {html_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--vault_name")
    parser.add_argument("--themes")
    parser.add_argument("--style", default='shanshui')
    args = parser.parse_args()
    
    if args.themes:
        themes = json.loads(args.themes)
    else:
        with open(Path(args.output) / "themes.json", 'r', encoding='utf-8') as f:
            themes = json.load(f)
            
    generate_immersive_html(args.output, args.vault_name, themes, args.style)
