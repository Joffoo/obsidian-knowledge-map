---
name: obsidian-knowledge-map
version: 2.2
description: 根据 Obsidian 笔记库内容，使用本地或在线获取的 ONNX 嵌入模型生成具有 AI 语义分类功能的知识地图（PNG/HTML）。触发词包括“生成知识地图”、“Knowledge Map”、“绘制笔记地形图”。
---

# Obsidian Knowledge Map Generator

该 Skill 通过“空间计算 - 语义归纳 - 艺术渲染 - 交互增强”四阶段流水线，将笔记库转化为可视化的语义地貌图。

## 环境定位 (Context Awareness)
- **脚本探测**：Agent 应优先通过 `glob("**/obsidian-knowledge-map/scripts/generator.py")` 确定脚本位置。
- **模型探测与自适配策略**：
  1. **零配置自动探测**：脚本按优先级自动寻找嵌入模型：
     - 命令行参数 `--model <path>`
     - 环境变量 `KNOWLEDGE_MAP_MODEL_DIR`
     - 本地私有配置文件 `config.json`（参考 `config.example.json`）
     - 技能内置便携目录 `<SKILL_DIR>/models/jina-embeddings-v2-base-zh`
     - 系统缓存目录 `~/.cache/obsidian-knowledge-map/models/jina-embeddings-v2-base-zh`
  2. **一键自动下载**：若本地无可用模型，执行配套脚本从镜像站极速拉取量化文件：
     ```powershell
     python "{SKILL_DIR}\scripts\setup_model.py"
     ```
     （如需指定到其他非系统盘存放，可追加参数：`--target-dir "D:\Models\jina-embeddings-v2-base-zh"`）。

## 核心流程

### 0. 预检与环境验证 (Pre-check)
在启动前，必须验证依赖：
1. **依赖检查**：执行 `python -c "import onnxruntime, umap, tokenizers, matplotlib, scipy, numpy, yaml, plotly"`。
2. **主动修复**：若报错，提供安装指令：`pip install onnxruntime umap-learn tokenizers matplotlib scipy numpy PyYAML plotly`。
3. **模型检查**：若未配置过模型，建议先执行 `python "{SKILL_DIR}\scripts\setup_model.py"` 或在 `config.json` 中配置现有路径。

### 1. 初始化与参数确认
确认目标笔记库路径 `vault_path` 及导出目录 `output_dir`。
> 💡 **参数与交互优化**：
> 1. **模型免输**：若本地已配置 `config.json` 或环境变量，**无需重复向用户询问模型路径**，直接调用即可。
> 2. **风格预选免问**：生成的交互式 HTML 页面右上角已**原生内置实时风格切换下拉菜单**（支持宋代山水、工程蓝图、深空星云、瑞士极简、和纸若竹、达芬奇手稿、现代极夜 7 大风格瞬时无缝切换），**无需在生成前向用户提问风格**！默认以 `shanshui` 作为初始视图全量生成。

### 2. 空间分析阶段 (Phase 1)
执行降维与聚类：
```powershell
python "{SCRIPT_PATH}" --mode analyze --vault "{vault_path}" --output "{output_dir}" --style "{style}"
```
**关键检查点**：确认生成了 `map_state.json`。

### 3. AI 语义归纳阶段 (Phase 2)
- 为 6 组标题总结名词短语分类标签。
- **输出要求**：必须将标签转换为 **JSON 列表字符串**，例如：`'["标签1", "标签2", ...]'`。

### 4. 艺术渲染阶段 (Phase 3)
执行绘图 (PNG)：
```powershell
python "{SCRIPT_PATH}" --mode render --vault "{vault_path}" --output "{output_dir}" --style "{style}" --themes '{themes_json}'
```
**渲染后自检 (Accessibility & Craft Audit)**：
- **风格自洽**：字体、徽标、底色与散点色盘是否与所选 style 高度契合。
- **对比度与清晰度**：深色背景散点带发光/浅色描边，浅色背景带有沉静墨色层次。

### 5. 交互增强阶段 (Phase 4 - 可选)
询问用户：“是否生成支持点击跳转的交互式 HTML 地图？”
若用户同意，执行：
```powershell
python "{SKILL_DIR}\scripts\html_generator.py" --output "{output_dir}" --vault_name "{vault_name}" --themes '{themes_json}' --style "{style}"
```

## 故障排除 (Troubleshooting)
- **内存不足**：若 Python 进程被 kill，建议用户关闭其他占用内存的程序后再试。
- **路径包含中文**：在 Windows PowerShell 中，变量传参时请确保使用双引号包裹。
- **模型格式错误**：若提示找不到 ONNX 文件，请确认路径指向包含 `tokenizer.json` 及 `model_quantized.onnx`（或子目录 `onnx/`）的文件夹。

## 注意事项
- **HTML 联动**：HTML 地图支持点击节点通过 `obsidian://` 协议直接打开笔记。
- **设计标准**：全面接入 `huashu-design` 规范与反 AI slop 调色逻辑，杜绝默认 tab20 色盘。
