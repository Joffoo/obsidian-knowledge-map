---
name: obsidian-knowledge-map
version: 2.4
description: 根据 Obsidian 笔记库内容，使用在线嵌入 API（OpenAI/SiliconFlow/Ollama 等兼容接口）或本地 ONNX 嵌入模型生成具有 AI 语义分类功能的知识地图（PNG/HTML）。触发词包括“生成知识地图”、“Knowledge Map”、“绘制笔记地形图”。
---

# Obsidian Knowledge Map Generator

该 Skill 通过“空间计算 - 语义归纳 - 艺术渲染 - 交互增强”四阶段流水线，将笔记库转化为可视化的语义地貌图。支持 **在线 API 极速模式** 与 **本地 ONNX 离线模式** 双引擎。

## 引擎架构与优先级 (Embedding Engine)

1. **在线 API 模式 (推荐)**：
   - 兼容 OpenAI 格式 `/v1/embeddings`（如 SiliconFlow 硅基流动、DeepSeek、OpenAI、本地 Ollama 等）。
   - **零重量级环境依赖**，速度极快（秒级响应），不消耗本机 CPU/显存。
2. **本地 ONNX 离线模式**：
   - 100% 本地运算，基于 `onnxruntime` + `tokenizers`，离线加载本地模型（如 `bge-m3`、`jina-embeddings-v2-base-zh`）。
   - 具备 JIT 自动静默就绪机制。

**配置解析层级**：
显式 CLI 传参（`--provider` / `--api-base` / `--api-key` / `--model-name` / `--model`） $\to$ 环境变量 $\to$ 私有配置文件 `config.json` $\to$ 便携/本地缓存目录。

## Agent 执行规范 (Agent Guidelines)

1. **隐私安全铁律**：API Key 与私密凭证**仅**允许保存在已配置 gitignore 的 `config.json` 或环境变量中，**严禁**硬编码进代码或提交到任何 Git 仓库中。
2. **自愈与免打扰**：
   - 若系统已存在有效配置（`config.json` 或环境变量），直接静默执行，零干扰交付。
   - 若为全新环境且没有任何配置，主动提供一次清晰的选择引导（在线 API 模式 vs 本地离线模式），获取配置后写入 `config.json`，后续即可全自动运行。
3. **容错与自愈式依赖**：
   - 降维引擎支持多算法自动降级（UMAP $\to$ t-SNE $\to$ PCA $\to$ SVD）。
4. **端到端全自动交付**：无需询问用户是否生成交互 HTML 或选择视觉风格，全流程自动串联分析、AI 标签总结与 HTML 生成，最终直接交付可点击的交互网页。

## 核心流程

### 0. 预检与环境验证 (Pre-check)
启动前由 Agent 自主执行依赖检查与安装：
```powershell
pip install matplotlib scipy numpy PyYAML plotly scikit-learn
```
（注：若使用本地 ONNX 模式，还需安装 `onnxruntime tokenizers`；若使用在线 API 模式，则无需额外依赖）。

### 1. 空间分析阶段 (Phase 1)
由 Agent 自动执行降维与聚类（参数全自动解析）：
```powershell
python "{SCRIPT_PATH}" --mode analyze --vault "{vault_path}" --output "{output_dir}"
```
如需强制刷新重算嵌入向量，可添加 `--force` 参数。
**检查点**：命令退出码为 0，且输出目录生成了 `map_state.json`。

### 2. AI 语义归纳阶段 (Phase 2)
- 脚本执行输出包含聚类近邻笔记标题。
- Agent 为各核心聚类总结 2~4 字的精炼中文名词短语标签。
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
