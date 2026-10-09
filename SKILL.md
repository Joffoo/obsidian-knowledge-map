---
name: obsidian-knowledge-map
version: 2.3
description: 根据 Obsidian 笔记库内容，使用本地或在线获取的 ONNX 嵌入模型生成具有 AI 语义分类功能的知识地图（PNG/HTML）。触发词包括“生成知识地图”、“Knowledge Map”、“绘制笔记地形图”。
---

# Obsidian Knowledge Map Generator

该 Skill 通过“空间计算 - 语义归纳 - 艺术渲染 - 交互增强”四阶段流水线，将笔记库转化为可视化的语义地貌图。

## Agent 自主执行铁律 (Agent Autonomous Rules)
> ⚠️ **零用户干预原则**：用户不需要也不会自行解决任何技术问题或配置路径。Agent 必须自主自愈、全程闭环。
1. **绝不向用户索要模型路径**：脚本内置了本地私有配置、环境变量、本地缓存及 **JIT（即时静默自动就绪）下载机制**，未配置模型时脚本会自动拉取并配置，禁止在对话中询问用户 `model_path`。
2. **容错与自愈式依赖安装**：脚本内置“多算法自动降级机制”（UMAP $\to$ t-SNE $\to$ PCA $\to$ SVD）。若环境缺少 `umap-learn` 或 C++ 编译环境报错，无需打扰用户，脚本会自动切换至预编译算法无缝完成。
3. **端到端全自动交付**：无需询问用户是否生成交互 HTML 或选择视觉风格，全流程自动串联分析、AI 标签总结与 HTML 生成，最终直接交付可点击的交互网页。

## 环境定位 (Context Awareness)
- **脚本探测**：Agent 应优先通过 `glob("**/obsidian-knowledge-map/scripts/generator.py")` 确定脚本位置。
- **模型管理**：脚本自动按顺序解析模型路径（显式传参 $\to$ 环境变量 $\to$ `config.json` $\to$ 便携目录 $\to$ 镜像自动拉取）。

## 核心流程

### 0. 预检与环境验证 (Pre-check)
启动前由 Agent 自主执行依赖检查与安装：
```powershell
pip install onnxruntime tokenizers matplotlib scipy numpy PyYAML plotly scikit-learn
```
（注：`umap-learn` 可尝试安装；若用户系统因缺失 C++ 编译器导致安装失败，直接跳过即可，系统会自动降级到 `scikit-learn`/内置 SVD 引擎）。

### 1. 空间分析阶段 (Phase 1)
由 Agent 自动执行降维与聚类（无需传递 `--model`，脚本全自动托管）：
```powershell
python "{SCRIPT_PATH}" --mode analyze --vault "{vault_path}" --output "{output_dir}"
```
**检查点**：命令退出码为 0，且输出目录生成了 `map_state.json`。

### 2. AI 语义归纳阶段 (Phase 2)
- 脚本执行输出包含聚类近邻笔记标题。
- Agent 为 6 组核心聚类总结 2~4 字的精炼中文名词短语标签。
- **输出格式**：转换为标准 JSON 字符串，例如：`'["AI Agent", "认知哲学", "项目管理", ...]'`。

### 3. 艺术与交互渲染 (Phase 3 & Phase 4)
Agent 自动连续执行静态图与交互 HTML 生成：
```powershell
python "{SCRIPT_PATH}" --mode render --vault "{vault_path}" --output "{output_dir}" --themes '{themes_json}'
python "{SKILL_DIR}\scripts\html_generator.py" --output "{output_dir}" --vault_name "{vault_name}" --themes '{themes_json}'
```

### 4. 交付与呈现
直接向用户交付：
1. **静态地形图**：`{output_dir}/knowledge_map.png`
2. **交互式 HTML**：`{output_dir}/knowledge_map.html`（附带右上角 7 大风格下拉切换器和笔记唤起协议说明）。
