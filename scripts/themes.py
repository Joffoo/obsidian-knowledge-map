"""
Obsidian Knowledge Map - Design System & Theme Presets
Crafted with huashu-design aesthetic standards & anti-AI-slop philosophy.
"""

THEMES = {
    'davinci': {
        'id': 'davinci',
        'name': '文艺复兴手稿 (Da Vinci)',
        'bg_color': '#f4ecd8',
        'ink_color': '#4e342e',
        'secondary_color': '#8c6d62',
        'accent_color': '#966432',
        'contour_levels': 20,
        'contour_alpha': 0.6,
        'contour_line_alpha': 0.35,
        'contour_line_width': 0.5,
        'cmap_colors': ['#f4ecd8', '#e2d3b3', '#c9a96e', '#8c5828', '#4e342e'],
        'plotly_colorscale': [
            [0.0, 'rgba(244, 236, 216, 0.0)'],
            [0.1, 'rgba(208, 208, 230, 0.25)'],
            [0.35, 'rgba(230, 208, 150, 0.45)'],
            [0.65, 'rgba(150, 100, 50, 0.55)'],
            [1.0, 'rgba(78, 52, 46, 0.75)']
        ],
        'scatter_palette': [
            '#8B4513', '#A0522D', '#CD853F', '#D2691E', '#B8860B',
            '#556B2F', '#6B8E23', '#4682B4', '#5F9EA0', '#483D8B',
            '#8FBC8F', '#BC8F8F', '#708090', '#2F4F4F', '#9932CC'
        ],
        'scatter_edge_color': 'none',
        'font_family_plt': ['Microsoft YaHei', 'SimSun', 'Times New Roman', 'Georgia', 'serif'],
        'font_family_web': "'Times New Roman', 'Baskerville', 'STSong', serif",
        'peak_markers': ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'],
        'peak_badge_type': 'roman_circle',
        'brand_title_format': "{vault_name} CARTOGRAPHY",
        'brand_subtitle': "RENAISSANCE CODEX & TOPOLOGY",
        'html_custom_css': """
            #brand {
                letter-spacing: 10px;
                font-family: 'Times New Roman', 'STSong', serif;
                text-transform: uppercase;
                opacity: 0.7;
            }
        """
    },

    'contemporary': {
        'id': 'contemporary',
        'name': '现代极夜深蓝 (Contemporary)',
        'bg_color': '#050505',
        'ink_color': '#FFFFFF',
        'secondary_color': '#94A3B8',
        'accent_color': '#00F0FF',
        'contour_levels': 20,
        'contour_alpha': 0.65,
        'contour_line_alpha': 0.25,
        'contour_line_width': 0.5,
        'cmap_colors': ['#0a0a0a', '#007aff', '#00ffff'],
        'plotly_colorscale': [
            [0.0, 'rgba(5, 5, 5, 0.0)'],
            [0.15, 'rgba(10, 30, 80, 0.2)'],
            [0.4, 'rgba(0, 100, 220, 0.45)'],
            [0.75, 'rgba(0, 180, 255, 0.65)'],
            [1.0, 'rgba(0, 255, 255, 0.85)']
        ],
        'scatter_palette': [
            '#38BDF8', '#818CF8', '#C084FC', '#F472B6', '#FB7185',
            '#34D399', '#4ADE80', '#A3E635', '#FACC15', '#FB923C',
            '#2DD4BF', '#60A5FA', '#A78BFA', '#E879F9', '#F43F5E'
        ],
        'scatter_edge_color': '#FFFFFF',
        'font_family_plt': ['Microsoft YaHei', 'SimHei', 'Inter', 'sans-serif'],
        'font_family_web': "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        'peak_markers': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'],
        'peak_badge_type': 'hud_dot',
        'brand_title_format': "{vault_name} CONTOUR",
        'brand_subtitle': "SYNTHETIC RADAR & DENSITY ATLAS",
        'html_custom_css': """
            #brand {
                letter-spacing: 12px;
                font-family: 'Inter', sans-serif;
                font-weight: 200;
                opacity: 0.6;
            }
        """
    },

    'shanshui': {
        'id': 'shanshui',
        'name': '宋代青绿山水 (Shanshui)',
        'bg_color': '#ECE7DE',  # 沉静古纸色，温润不刺眼
        'ink_color': '#1C2321',  # 松烟焦墨
        'secondary_color': '#5C6764',
        'accent_color': '#9E2A2B',  # 朱砂印泥红（点睛）
        'contour_levels': 24,
        'contour_alpha': 0.65,
        'contour_line_alpha': 0.35,
        'contour_line_width': 0.45,
        'cmap_colors': ['#ECE7DE', '#A3C1AD', '#5B8A72', '#235789', '#1C2321'],  # 沉静古纸 -> 初树浅绿 -> 叠翠石绿 -> 苍山石青 -> 峰峦焦墨
        'plotly_colorscale': [
            [0.0, 'rgba(236, 231, 222, 0.0)'],
            [0.12, 'rgba(217, 226, 236, 0.3)'],
            [0.35, 'rgba(163, 193, 173, 0.45)'],
            [0.65, 'rgba(91, 138, 114, 0.6)'],
            [0.85, 'rgba(35, 87, 137, 0.75)'],
            [1.0, 'rgba(28, 35, 33, 0.85)']
        ],
        # 传统国画天然矿物颜料调色板
        'scatter_palette': [
            '#9E2A2B', '#235789', '#5B8A72', '#D4A373', '#774936',
            '#3A5A40', '#6A4C93', '#1982C4', '#8AC926', '#FF595E',
            '#C57B57', '#463F3A', '#2E4057', '#9381FF', '#B8833B'
        ],
        'scatter_edge_color': '#1C2321',
        'font_family_plt': ['Songti SC', 'STSong', 'SimSun', 'Microsoft YaHei', 'serif'],
        'font_family_web': "'Songti SC', 'STSong', 'Noto Serif SC', 'SimSun', serif",
        'peak_markers': ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'],
        'peak_badge_type': 'stamp',  # 印章风格
        'brand_title_format': "{vault_name} · 知识千里江山图",
        'brand_subtitle': "高维语义叠嶂 · 文人界画图卷",
        'html_custom_css': """
            #brand {
                letter-spacing: 8px;
                font-family: 'Songti SC', 'STSong', 'SimSun', serif;
                font-weight: 500;
                color: rgba(28, 35, 33, 0.7);
            }
            .stamp-box {
                border: 1.5px solid #9E2A2B;
                color: #9E2A2B;
                padding: 2px 6px;
                font-weight: bold;
                border-radius: 2px;
                background: rgba(236, 231, 222, 0.85);
            }
        """
    },

    'blueprint': {
        'id': 'blueprint',
        'name': '普鲁士工程蓝图 (Blueprint)',
        'bg_color': '#0A192F',  # 经典普鲁士蓝
        'ink_color': '#E2F1FF',  # 高亮白图线
        'secondary_color': '#64B5F6',
        'accent_color': '#00F0FF',  # 测绘激光青
        'contour_levels': 22,
        'contour_alpha': 0.7,
        'contour_line_alpha': 0.45,
        'contour_line_width': 0.5,
        'cmap_colors': ['#071526', '#133E68', '#0E7490', '#06B6D4', '#E0F2FE'],  # 深蓝基准 -> 拓扑深蓝 -> 结构青 -> 高亮青 -> 蓝白核心
        'plotly_colorscale': [
            [0.0, 'rgba(10, 25, 47, 0.0)'],
            [0.15, 'rgba(19, 62, 104, 0.25)'],
            [0.4, 'rgba(14, 116, 144, 0.5)'],
            [0.7, 'rgba(6, 182, 212, 0.7)'],
            [1.0, 'rgba(224, 242, 254, 0.9)']
        ],
        # 工业 CAD / 仪表盘高辨识度调色板
        'scatter_palette': [
            '#00F0FF', '#38BDF8', '#34D399', '#FBBF24', '#F472B6',
            '#A78BFA', '#FB7185', '#60A5FA', '#2DD4BF', '#FDE047',
            '#E2E8F0', '#818CF8', '#C084FC', '#4ADE80', '#F87171'
        ],
        'scatter_edge_color': '#E2F1FF',
        'font_family_plt': ['JetBrains Mono', 'Consolas', 'Courier New', 'Microsoft YaHei', 'monospace'],
        'font_family_web': "'JetBrains Mono', 'SF Mono', 'Consolas', monospace",
        'peak_markers': ['SEC-01', 'SEC-02', 'SEC-03', 'SEC-04', 'SEC-05', 'SEC-06', 'SEC-07', 'SEC-08', 'SEC-09', 'SEC-10'],
        'peak_badge_type': 'crosshair',  # 瞄准十字线
        'brand_title_format': "{vault_name} // SYSTEM SCHEMATIC",
        'brand_subtitle': "TOPOLOGICAL DENSITY MAP · SPECIFICATION V2.0",
        'html_custom_css': """
            body::before {
                content: "";
                position: absolute;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background-image: 
                    linear-gradient(rgba(226, 241, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(226, 241, 255, 0.03) 1px, transparent 1px);
                background-size: 30px 30px;
                pointer-events: none;
                z-index: 10;
            }
            #brand {
                letter-spacing: 6px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                color: #64B5F6;
                opacity: 0.85;
            }
        """
    },

    'stellar': {
        'id': 'stellar',
        'name': '深空韦伯星云 (Stellar)',
        'bg_color': '#040208',  # 宇宙深空极黑
        'ink_color': '#F3E8FF',  # 星光冷银
        'secondary_color': '#C084FC',
        'accent_color': '#F43F5E',  # 超新星洋红
        'contour_levels': 24,
        'contour_alpha': 0.7,
        'contour_line_alpha': 0.3,
        'contour_line_width': 0.4,
        'cmap_colors': ['#0A0612', '#3B0764', '#831843', '#DB2777', '#FEF08A'],  # 真空黑紫 -> 紫外星云 -> 电离氢深洋红 -> 激波粉红 -> 超新星炽金
        'plotly_colorscale': [
            [0.0, 'rgba(4, 2, 8, 0.0)'],
            [0.15, 'rgba(59, 7, 100, 0.25)'],
            [0.45, 'rgba(131, 24, 67, 0.5)'],
            [0.75, 'rgba(219, 39, 119, 0.7)'],
            [1.0, 'rgba(254, 240, 138, 0.9)']
        ],
        # 恒星光谱色盘（热白矮星、年轻蓝星、红巨星、脉冲星）
        'scatter_palette': [
            '#38BDF8', '#818CF8', '#E879F9', '#F43F5E', '#FB923C',
            '#FDE047', '#A78BFA', '#2DD4BF', '#4ADE80', '#F472B6',
            '#E0E7FF', '#C084FC', '#FB7185', '#34D399', '#60A5FA'
        ],
        'scatter_edge_color': '#FFFFFF',
        'font_family_plt': ['Microsoft YaHei', 'Inter', 'Segoe UI', 'sans-serif'],
        'font_family_web': "'Inter', 'Space Grotesk', -apple-system, sans-serif",
        'peak_markers': ['α-ORI', 'β-CYG', 'γ-CAS', 'δ-SCO', 'ε-PEG', 'ζ-TAU', 'η-UMA', 'θ-AUR', 'ι-LEO', 'κ-AQL'],
        'peak_badge_type': 'star',
        'brand_title_format': "{vault_name} // CELESTIAL DEEP FIELD",
        'brand_subtitle': "INTERSTELLAR SEMANTIC NEBULA SURVEY",
        'html_custom_css': """
            #brand {
                letter-spacing: 14px;
                font-family: 'Inter', sans-serif;
                font-weight: 200;
                color: #C084FC;
                opacity: 0.75;
                text-shadow: 0 0 12px rgba(192, 132, 252, 0.4);
            }
        """
    },

    'swiss': {
        'id': 'swiss',
        'name': '瑞士国际主义 (Swiss Minimal)',
        'bg_color': '#F8F8F8',  # 纯净极简哑光灰白
        'ink_color': '#111111',  # 炭黑墨
        'secondary_color': '#555555',
        'accent_color': '#E60000',  # 纯正经典瑞士红（关键点睛）
        'contour_levels': 20,
        'contour_alpha': 0.65,
        'contour_line_alpha': 0.4,
        'contour_line_width': 0.6,
        'cmap_colors': ['#EAEAEA', '#C4C4C4', '#888888', '#383838', '#111111'],  # 纯粹现代木刻灰阶
        'plotly_colorscale': [
            [0.0, 'rgba(248, 248, 248, 0.0)'],
            [0.15, 'rgba(220, 220, 220, 0.3)'],
            [0.4, 'rgba(160, 160, 160, 0.5)'],
            [0.75, 'rgba(80, 80, 80, 0.7)'],
            [1.0, 'rgba(17, 17, 17, 0.85)']
        ],
        # 瑞士高反差排版调色板：纯正黑灰对比，以瑞士红点睛
        'scatter_palette': [
            '#E60000', '#111111', '#4A4A4A', '#737373', '#999999',
            '#262626', '#B30000', '#D63031', '#595959', '#333333',
            '#8C8C8C', '#A6A6A6', '#1A1A1A', '#FF3838', '#666666'
        ],
        'scatter_edge_color': '#111111',
        'font_family_plt': ['Helvetica Neue', 'Arial', 'Microsoft YaHei', 'sans-serif'],
        'font_family_web': "'Helvetica Neue', Arial, 'Inter', -apple-system, sans-serif",
        'peak_markers': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10'],
        'peak_badge_type': 'swiss_box',
        'brand_title_format': "{vault_name} · KARTOGRAPHIE",
        'brand_subtitle': "INTERNATIONALE TYPOGRAFIE & ORDNUNG",
        'html_custom_css': """
            #brand {
                letter-spacing: 5px;
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-weight: 800;
                color: #111111;
                border-left: 3px solid #E60000;
                padding-left: 12px;
                opacity: 0.9;
            }
        """
    },

    'matcha': {
        'id': 'matcha',
        'name': '和纸苔藓若竹 (Matcha & Bamboo)',
        'bg_color': '#F6F4EB',  # 柔和手工和纸
        'ink_color': '#243328',  # 浓煎深焙茶绿
        'secondary_color': '#4E6E58',
        'accent_color': '#B86B35',  # 浅赭木质暖色
        'contour_levels': 22,
        'contour_alpha': 0.65,
        'contour_line_alpha': 0.35,
        'contour_line_width': 0.45,
        'cmap_colors': ['#E2E7E1', '#A3B899', '#668067', '#344E41', '#1A2E22'],  # 初露水色 -> 若竹浅绿 -> 宇治抹茶青 -> 深苔古绿 -> 浓翠墨绿
        'plotly_colorscale': [
            [0.0, 'rgba(246, 244, 235, 0.0)'],
            [0.15, 'rgba(226, 231, 225, 0.3)'],
            [0.4, 'rgba(163, 184, 153, 0.45)'],
            [0.7, 'rgba(102, 128, 103, 0.65)'],
            [1.0, 'rgba(36, 51, 40, 0.85)']
        ],
        # 传统和风低饱和草木矿物色盘
        'scatter_palette': [
            '#344E41', '#588157', '#A3B899', '#B86B35', '#6B705C',
            '#A5A58D', '#DDA15E', '#BC6C25', '#283618', '#606C38',
            '#839788', '#EEE2DF', '#735D78', '#B388EB', '#4A5759'
        ],
        'scatter_edge_color': '#243328',
        'font_family_plt': ['Microsoft YaHei', 'STSong', 'Yu Mincho', 'Hiragino Mincho ProN', 'serif'],
        'font_family_web': "'Yu Mincho', 'Hiragino Mincho ProN', 'STSong', 'Noto Serif SC', serif",
        'peak_markers': ['壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '拾'],
        'peak_badge_type': 'zen_circle',
        'brand_title_format': "{vault_name} · 知識の庭園",
        'brand_subtitle': "ZEN GARDEN TOPOGRAPHY · 苔庭地勢図",
        'html_custom_css': """
            #brand {
                letter-spacing: 8px;
                font-family: 'Yu Mincho', 'STSong', serif;
                font-weight: 400;
                color: #243328;
                opacity: 0.8;
            }
        """
    }
}

def get_theme(style_name):
    """
    Safely retrieve theme configuration. Defaults to 'davinci' if style not found.
    """
    if not style_name or style_name.lower() not in THEMES:
        return THEMES['davinci']
    return THEMES[style_name.lower()]
