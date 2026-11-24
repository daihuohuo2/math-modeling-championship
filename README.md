# math-modeling-championship

数学建模竞赛（CUMCM 国赛 / MCM-ICM 美赛等）端到端 AI 工作流：从选题审题、数据审计、建模求解、代码复现、图表制作，到论文写作排版、提交合规与 **15 位专家复评闭环（平均分 ≥92 才放行）**。

> 92 分是内部放行线，不是获奖预测。论文是否提交、如何使用 AI 辅助，由队伍自行承担合规责任。

## 特性

- **阶段门禁**：M1 建模终检 / P1 最小可运行结果 / P2 编程终检 / W1 证据大纲 / W2 论文终检，五道独立质检 Subagent 门禁嵌在阶段转折点，不等终稿才验收。
- **不可博弈的评分聚合**：`aggregate_panel.py` 代码级强制 15 个唯一视角、独立性确认、冻结版本 SHA-256 绑定、未舍入均值；`validate_submission.py` 做最终确定性放行。
- **评阅校准**：评分权重与原子扣分法锚定真实国赛评阅流程（`references/评阅校准.md`）。
- **数据泄漏设防**：外部数据隔离状态机、按物理实体定义实验单元（`references/data-model-quality.md`）。
- **2026 合规模板**：内置无目录、含 AI 使用声明、页数结构合规的 LaTeX 基线模板（`tools/latex/assets/templates/cumcm-2026/`）。
- **Checkpoint V1 保底**：先产出物理可提交版本再优化，92 分门禁与截止时间兼容（`references/delivery-deadline.md`）。
- **三档运行模式**：fast / standard / championship 按剩余时间推荐与切换，砍广度不砍底线（`references/运行模式.md`）。

## 安装

### Claude Code / ZCode（用户级 skill）

PowerShell：

```powershell
.\scripts\install.ps1
```

或手动复制整个目录到：

- Windows：`%USERPROFILE%\.agents\skills\math-modeling-championship\`
- macOS / Linux：`~/.agents/skills/math-modeling-championship/`

### Codex CLI

复制到 `$HOME/.agents/skills/math-modeling-championship/`；`agents/openai.yaml` 提供发现元数据。

### 环境要求

- Python ≥ 3.9（建议 3.12）；`pip install numpy scipy pandas matplotlib openpyxl pypdf`
- LaTeX（xelatex + ctex，MiKTeX 或 TeX Live）；需要 Word 交付时另装 Pandoc
- 运行 `python scripts/doctor.py --project <PROJECT_ROOT>` 查看完成度清单

## 使用

对已安装并启用本 skill 的 Agent（Claude Code / ZCode / Codex）直接说：

- "用 math-modeling-championship 做完这道题"：完整流程
- "只做题目分析和模型选择" / "只写论文"：单阶段任务，只跑对应门禁
- "切到 fast" / "升级到 championship"：切换运行模式
- "看进度"：输出当前阶段、门禁状态、panel 分数、Checkpoint 状态

启动后 Agent 会报告 `SKILL_ROOT`、`PROJECT_ROOT`、竞赛/届次/题号并核验当届规则；所有新产物只写入你的项目目录。

## 目录导航

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 主入口：启动协议、路由表、质量原则、交付物合同 |
| `references/` | 工作流、角色、评阅校准、运行模式、2026 格式规范、数据质量、提交合规 |
| `references/roles/` | 建模手 / 编程手 / 论文手三角色的 SKILL.md 与细则 |
| `scripts/` | `init_project.py`、`doctor.py`、`aggregate_panel.py`、`validate_submission.py` |
| `assets/` | 算法资料、状态模板、获奖论文基准目录（`exemplars/`，只读） |
| `tools/` | pdf / xlsx / docx / latex / figure / paper_search 六个工具子包 |
| `examples/` | 端到端示例的产物布局说明 |

## 来源

本项目在 [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) 的基础上重构，沿用了部分角色资料、算法说明与工具。

## 许可与免责

- `tools/docx/` 内含第三方组件，见 `tools/docx/LICENSE.txt`。
- 本 skill 输出的论文是**草稿质量的候选成果**：提交前必须由队伍人工核对、修改并承担最终责任。真实竞赛请遵守当届规则与所在学校/赛区的 AI 使用规定，如实完成 AI 使用披露。
