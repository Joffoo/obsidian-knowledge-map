# Obsidian Knowledge Map | Obsidian 语义知识地图

[English](#english) | [中文](#chinese)

---

<a name="english"></a>

## English

**Obsidian Knowledge Map** is an advanced skill that visualizes your Obsidian vault as an interactive, multi-themed semantic landscape. By combining local embedding computation with sophisticated design systems, it turns high-dimensional notes into a living topographic atlas.

### ✨ Key Features (v2.1)

-   **Embedding-Based Clustering**: Computes note embeddings with `jina-embeddings-v2` via ONNX and projects high-dimensional semantic spaces onto a 2D plane with adaptive UMAP.
-   **KDE Topographic Field**: Computes 80-layer continuous elevation density contours using Gaussian Kernel Density Estimation.
-   **AI Semantic Synthesis**: Summarizes high-level category titles for prominent semantic peaks across vault clusters.
-   **7 Comprehensive Design Systems (Anti-AI-Slop)**:
    -   🏯 **Shanshui (宋代青绿山水)**: Warm Xuan paper parchment, mineral green/blue gradients, pine-soot ink, cinnabar seal stamps, and Chinese heavenly stems.
    -   📐 **Blueprint (普鲁士工程蓝图)**: Prussian deep blue `#0A192F`, technical cyan highlights, crosshair survey markers, and 30px drafting grid lines.
    -   🌌 **Stellar (深空韦伯星云)**: Cosmic void black, glowing supernova magenta/gold, stellar spectral palettes, and celestial badges.
    -   🟥 **Swiss (瑞士国际主义)**: Matte high-contrast woodblock greyscale, stark typographic grid, accented by pure Swiss Red (`#E60000`).
    -   🍵 **Matcha (和纸苔藓若竹)**: Organic Japanese Washi paper, soothing bamboo/matcha greens, Morandi earth minerals, and gentle circular badges.
    -   📜 **Da Vinci (文艺复兴手稿)**: Vintage parchment, sepia ink, and classical Roman numeral codex styling.
    -   📟 **Contemporary (现代极夜深蓝)**: Dark cyber sonar radar, electric cyan thermals, and minimalist typography.
-   **Interactive Web App with Live Theme Switcher**:
    -   **Top-Right Floating Capsule**: Switch between all 7 themes on the fly inside the browser with zero reload and millisecond responsiveness.
    -   **Deep Linking to Obsidian**: Click on any note node to immediately open the note in your Obsidian app via `obsidian://open`.
    -   **Smart Preference Memory**: Remembers your preferred style via `localStorage`.

### 🚀 Workflow

1.  **Spatial Computation**: Extracts vault notes, executes embedding inference, and runs adaptive UMAP + KDE peak detection.
2.  **Semantic Synthesis**: The Agent analyzes nearest neighbor titles around detected peaks to generate concise topic tags.
3.  **Static & Interactive Generation**:
    -   Generates submission-grade 14x14 HD static PNG maps.
    -   Generates standalone, self-contained interactive HTML maps with live theme switching.

### 🛠️ Installation

1.  Clone this repository into your skills directory:
    ```bash
    git clone https://github.com/fengyukongzhou/obsidian-knowledge-map.git .agent/skills/obsidian-knowledge-map
    ```
2.  Install dependencies:
    ```bash
    pip install onnxruntime umap-learn tokenizers matplotlib scipy numpy PyYAML plotly
    ```

---

<a name="chinese"></a>

## 中文

**Obsidian 语义知识地图** 是将 Obsidian 笔记库转化为交互式、多风格语义地貌图的高阶可视化技能。结合本地向量空间计算与专业级设计系统，将高维个人知识库沉淀为生动的地貌图卷。

### ✨ 核心特性 (v2.1)

-   **高维向量嵌入与降维**：利用 `jina-embeddings-v2` ONNX 模型提取笔记深层语义，自适应 UMAP 算法将高维特征平滑投影至 2D 平面。
-   **80 层连续等高线地貌**：基于高斯核密度估计（Gaussian KDE）构建平滑连绵的知识山峦与群岛地形。
-   **AI 峰位语义归纳**：智能提炼各个地貌山峰聚类中的核心主题与知识领域标签。
-   **7 大独立设计系统（拒绝 AI-Slop 通用模板）**：
    -   🏯 **宋代青绿山水 (`shanshui`)**：沉静宣纸暖灰白底、石青石绿矿物五层叠嶂、松烟焦墨、**朱砂印泥钤印**与天干编号。
    -   📐 **普鲁士工程蓝图 (`blueprint`)**：工程深蓝 `#0A192F`、高亮白图线、**测绘十字准星**、技术等宽排版与 30px 坐标底纹。
    -   🌌 **深空韦伯星云 (`stellar`)**：宇宙深黑 `#040208`、电离氢洋红与超新星炽金星云、恒星光谱发光色板与天体星标。
    -   🟥 **瑞士国际主义 (`swiss`)**：现代木刻高反差灰阶、非对称网格、以**纯正瑞士红 (`#E60000`)** 为唯一视觉焦点。
    -   🍵 **和纸苔藓若竹 (`matcha`)**：手工和纸柔底、宇治抹茶与若竹浅绿、和风草木矿物调色盘与护眼排版。
    -   📜 **文艺复兴手稿 (`davinci`)**：古典达芬奇羊皮纸手稿、深赭石墨线与罗马数字徽标。
    -   📟 **现代极夜深蓝 (`contemporary`)**：极夜黑底、电光青蓝热力、数字雷达。
-   **全屏交互式地图与实时风格切换**：
    -   **右上角磨砂玻璃胶囊**：无需刷新页面，在浏览器内**毫秒级随心切换 7 种风格**（等高线梯度、散点色盘、峰位徽章与排版瞬间重绘）。
    -   **Obsidian 深度联动**：点击任意散点笔记，秒级通过 `obsidian://open` 协议唤起本地 Obsidian 打开原文。
    -   **自动偏好记忆**：切换后通过 `localStorage` 自动记住喜好风格。

### 🚀 运行流程

1.  **空间计算**：扫描笔记库、计算嵌入向量与 UMAP 坐标，并执行 KDE 峰值检测生成地貌状态。
2.  **语义归纳**：Agent 分析聚类邻域笔记标题，总结代表性知识分类。
3.  **双端渲染**：
    -   生成 14×14 高清静态打印级 PNG 地貌图。
    -   生成免刷新实时切换风格的单文件交互式 HTML。

### 🛠️ 安装方法

1.  克隆本仓库至技能目录：
    ```bash
    git clone https://github.com/fengyukongzhou/obsidian-knowledge-map.git .agent/skills/obsidian-knowledge-map
    ```
2.  安装必要依赖：
    ```bash
    pip install onnxruntime umap-learn tokenizers matplotlib scipy numpy PyYAML plotly
    ```

---

**Designed with ❤️ & huashu-design standards.**
