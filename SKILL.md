---
name: math-modeling-championship
description: 数学建模竞赛端到端工作流：从选题审题、数据审计、建模求解、代码求解与复现、图表制作，到论文写作排版、支撑材料、AI 使用披露与 15 位专家复评闭环（平均分≥92 才放行）。当用户要求数学建模、建模竞赛、建模分析、代码求解、结果可视化、生成或修改竞赛论文与支撑材料，或从任意阶段继续、审查、返工一套可提交的竞赛成果时使用；也支持只执行单个阶段。不用于普通数学作业、一般数据分析或非竞赛论文润色。
---

# 数学建模竞赛全流程工作流

目标是交付证据可追溯、代码可复现、格式合规、经 15 个独立视角复评且平均分达到 92 分以上的竞赛论文与支撑材料。流程与质量门禁以本文件和 `references/` 为权威；生产细节（角色规范、算法资料、文档工具链）位于随附的 `references/roles/`、`references/算法索引.md`、`assets/` 和 `tools/`，按需加载。`92` 分是内部放行线，不是获奖预测或一等奖保证。

## 启动协议

首次激活时在进度更新中报告：

- `SKILL_ROOT`：本文件所在目录，只读；`PROJECT_ROOT`：用户项目目录，所有新产物只写这里；
- 竞赛名称、届次、题号、截止时间、论文语言与当前阶段；
- 已提供的赛题、附件、模板、规则、已有代码和论文；未核验的当届官方规则明确标为待核验；
- 本阶段计划读取的角色与工具入口。

优先读取已有 `PROJECT_ROOT/state/decision_log.json` 恢复进度。新项目运行：

```powershell
python "<SKILL_ROOT>/scripts/init_project.py" "<PROJECT_ROOT>" --competition "<竞赛>" --year "<届次>"
```

新项目或环境变化时立即运行 `python "<SKILL_ROOT>/scripts/doctor.py" --project "<PROJECT_ROOT>"` 输出完成度清单（Python、科学计算栈、xelatex、pdftotext、Pandoc、压缩器、项目目录）；缺关键组件时报告并请用户确认是否安装，不得静默跳过。

开始每个阶段前实际读取该阶段的入口文件（见路由表）；知道文件路径不等于已经执行。严格使用本 Skill 的脚本、模板与工具；已有工具可用时禁止为省时手写替代实现。环境缺少引擎、渲染器或依赖时，报告阻塞并继续完成仍可验证的部分，不得静默换工具或用较差产物冒充完成；任何校验预警都视为未完成。用户附件与官方模板只读，需修改时先复制到 `PROJECT_ROOT`，不得覆盖用户已有文件。离散的关键选择用编号问题让用户决定；只有缺失信息会显著改变题意、数据权限、提交合规或模型路线时才暂停询问。

## 路由表

| 任务 | 入口 |
|---|---|
| 完整竞赛流程 | [references/workflow.md](references/workflow.md) 按 Stage 0–10 推进，生产阶段调用对应角色入口 |
| 审题、建模、验证设计（Stage 2–4） | [references/roles/建模手/SKILL.md](references/roles/建模手/SKILL.md) |
| 代码实现、求解、出图（Stage 5–7） | [references/roles/编程手/SKILL.md](references/roles/编程手/SKILL.md) |
| 论文写作、排版、修改（Stage 8–9） | [references/roles/论文手/SKILL.md](references/roles/论文手/SKILL.md) |
| 选模型、查算法 | [references/算法索引.md](references/算法索引.md)，再读相关 `assets/0*.md` 算法说明 |
| 数据、泄漏、模型选择细则 | [references/data-model-quality.md](references/data-model-quality.md) |
| 论文结构、摘要、加粗、图表、自然表达 | [references/paper-quality.md](references/paper-quality.md) |
| 写作与评审前对齐获奖论文基准 | [assets/exemplars/README.md](assets/exemplars/README.md) |
| 15 专家评分与返工循环 | [references/expert-panel.md](references/expert-panel.md) |
| 真实评阅标准锚定（原子扣分法、权重结构） | [references/评阅校准.md](references/评阅校准.md) |
| 三档模式（fast/standard/championship）与降级 | [references/运行模式.md](references/运行模式.md) |
| 状态文件、目录合同、交付清单 | [references/state-deliverables.md](references/state-deliverables.md) |
| 当届规则、匿名、AI 披露、提交包 | [references/submission-compliance.md](references/submission-compliance.md) |
| CUMCM 2026 页数结构、无目录、非图片 PDF、AI 声明新口径 | [references/cumcm-2026-格式规范.md](references/cumcm-2026-格式规范.md) |
| 截止时间管理、Checkpoint V1 可提交保底 | [references/delivery-deadline.md](references/delivery-deadline.md) |
| 环境预检（Python/LaTeX/PDF 工具/压缩器） | `python "<SKILL_ROOT>/scripts/doctor.py" --project "<PROJECT_ROOT>"` |
| Subagent 协作与质检派发 | [references/Subagent调度.md](references/Subagent调度.md) |
| 读 PDF / Excel / 绘图 / Word / LaTeX / 文献检索 | `tools/<对应工具>/SKILL.md`，实际读取后再用 |

启动时按距内部内容冻结时间推荐运行模式（>12h `championship`、4–12h `standard`、<4h `fast`），用户可随时切换；任何档位下官方规则核验、真实运行、非图片 PDF、页数结构和 Checkpoint V1 不得跳过，详见 `references/运行模式.md`。

单阶段任务只运行对应阶段及其进入/退出门禁，不强制完整流程。处理 PDF、Excel、Word、LaTeX 或科研绘图时，必须实际读取对应工具入口后再调用。

## 角色与权威写入

按“建模手 → 编程手 → 论文手”顺序生产权威产物，主 Agent 统一裁决和写入：

- 建模手：题意、数据合同、候选模型、假设、符号、验证设计；交付《题目分析报告.md》《术语表格.md》；
- 编程手：可运行实现、真实结果、复现清单和三类证据图；
- 论文手：主张—证据大纲、正文、排版、引用、支撑材料与提交包；
- 独立质检者：只读审查，不直接修改权威产物；关键节点执行 M1/P1/P2/W1/W2 门禁。

不要让多个角色并行修改同一论文、代码或结果。若支持 Subagent，按阶段门禁和最终专家视角分批独立评审；各评审在提交分数前不得看到其他评审的分数和结论。环境不支持 Subagent 时只能报告受限交付，不得把主 Agent 自检描述为独立通过。

## 不可违反的质量原则

1. **官方规则优先**：当届官网、题面和官方模板高于本 Skill 的经验规则。Stage 0、Stage 8、Stage 10 都重新核验并记录来源、日期与文件哈希。
2. **证据先于文字**：所有结果、表格和摘要数字必须来自实际运行产物；缺证据就回退，不得补写或猜测。
3. **数据边界先冻结**：任何外部数据先分类为背景、协变量、训练标签、真实答案或辅助基准。会改变任务难度的外部标签/答案不得静默进入主方案；需用户同意、显著披露，并与仅用赛题数据的主线分开。
4. **独立样本按物理实体定义**：不得把行号、滑动窗口、同一对象的重复测量或续接批次当作独立样本。训练、调参和测试的分组必须阻断泄漏。
5. **复杂模型必须赢得复杂度**：与强基线做同一数据切分、同一指标的样本外比较；没有稳定增益就降级或删去复杂模型。
6. **作者自检、确定性脚本、独立质检互不替代**：固定成果在关键节点执行 M1、P1、P2、W1、W2；实质修改会使受影响的 PASS 失效。
7. **不伪装、不规避检测**：所谓“不过度 AI 化”是指表达具体、有作者判断、证据可核、图表克制并经人工复核；不得以绕过 AI 检测或隐瞒 AI 使用为目标。
8. **放行而非许愿**：只有当提交合规通过、无未解决致命问题、15 专家算术平均分 `>=92.00` 时，才标记 `submission_ready=true`。不得声称一定获奖。
9. **借鉴结构、拒绝抄袭**：获奖论文和往届作品只用于对齐结构、方法与图表规范；句式、段落组织、图表设计和模型组合必须重写，不得复用任何往届论文（含本队往届）的成段文字，借鉴的方法与数据必须标注引用。评委会做跨年查重，模板化摘要与复用文本按学术不端处理。
10. **CUMCM 2026 硬约束**：电子版第一页必须为摘要专用页，承诺书/编号专用页不得进入电子版；正文（正文主体 + AI 使用声明 + 参考文献）≤30 页、不要目录、页边距 ≥2.5cm、无任何身份信息；附录页数不限但必须含支撑材料清单与全部可运行源程序（无程序/无支撑材料须在附录声明）；参赛论文电子版为 PDF 或 Word 之一（建议 PDF）≤20MB 且不压缩；交付非图片 PDF（图片 PDF 按不成功参赛处理）；参考文献不再列 AI 条目，正文 AI 声明（须说明用途）与支撑材料 AI 使用详情必须保留。细则见 [references/cumcm-2026-格式规范.md](references/cumcm-2026-格式规范.md)，官方原文存档 `assets/format2026.doc`。

## 固定交付物

- **建模手**：《题目分析报告.md》《术语表格.md》，细目见其 SKILL.md；
- **编程手**：可运行的 Python（`.py`）或 MATLAB（`.m`）代码；结果表（`.csv` 或题目要求的 `.xlsx`）；原始数据图、模型过程图、最终结果图三类候选图——每个子问题每类至少 1 张、每类合计至少 3 张并覆盖全部子问题，文件名用 `raw_q1_*`、`process_q1_*`、`result_q1_*` 格式；`results/复现清单.json` 含随机种子、输入 SHA-256、依赖版本、关键参数和唯一复现命令；
- **论文手**：论文格式以当届规则为准——规则建议 PDF 时交付正式 PDF（LaTeX 编译或 Word 导出）并保留源文件；规则接受 Word 时默认交付 `完整论文.docx`（由 LaTeX 转换时保留哈希绑定的 `.conversion.json`）。用户明确要求 LaTeX 时双格式同交，正文内容、数据、图表和结论保持一致，附 `.build.json`。正文正式图默认至少 8 幅，与当届页数规则冲突时以规则为准并记录依据；
- **提交包**：提交文件、`submission_manifest.json`、复现清单、AI 使用披露和支撑材料压缩包，合同见 [references/state-deliverables.md](references/state-deliverables.md)。

内部检查记录不作为额外交付物。

## 反馈闭环

每阶段开头读状态，结尾写入采用与否、依据、被拒方案、产物路径、输入哈希、运行命令、指标、风险和下一门禁。发现冲突时只回退到最早受影响阶段：

- 数据来源、标签边界、实验单位或泄漏问题 → Stage 2/5；
- 模型假设、公式、约束或可识别性问题 → Stage 3/4；
- 实现、结果、验证、稳健性或不确定性问题 → Stage 5/6/7；
- 主张—证据、摘要、图表、语言或格式问题 → Stage 8/9；
- 规则、匿名、AI 披露或支撑材料问题 → Stage 0/10。

最终每轮专家评分写入 `review/panel_round_<N>.json`，然后运行：

```powershell
python "<SKILL_ROOT>/scripts/aggregate_panel.py" --input "<PROJECT_ROOT>/review/panel_round_<N>.json" --output "<PROJECT_ROOT>/state/panel_latest.json" --threshold 92
```

未通过时按专家证据做定向返工，重跑失效门禁并开始新一轮评分。平均分不得四舍五入后越线；以未舍入平均值比较。不得删除低分、重复高分或让同一视角评两次来凑门槛。若同一外部阻塞连续三轮仍无法消除，或缺少用户授权、官方材料或必要数据，应标记 `BLOCKED`、保留 92 分门槛并向用户说明，不得自行降标。

## 去 AI 化的真实表达

最终正文和图表必须做到“具体、有作者判断、证据可核”，消除机器生成感：

- **数字**：保留 2–3 位有效数字，极小值用科学计数法（如 `4.0×10⁻⁴`）；不出现 `0.0004123`、`18.0736%` 这类长尾精度。摘要每段以决策或结论收尾，不以统计量堆叠收尾；
- **图表**：统一科研风格，克制的色盲安全配色；禁用仪表盘拼贴、霓虹渐变、玻璃拟态、假 3D、装饰图标和默认彩虹色图；流程图用黑白线框即可，节点必须对应真实代码与决策；
- **语言**：删除“综上所述”“值得一提的是”“结果表明模型具有较强优越性”等模板句；术语、符号、单位全篇唯一；句长自然变化，允许短句；
- **边界**：不故意制造错别字或口语化来伪装人工，不以规避 AI 检测为目标；按当届规则如实生成 AI 使用披露（见 submission-compliance.md）。

执行细则与检查清单见 [references/paper-quality.md](references/paper-quality.md)。

## 最终门禁

冻结 PDF/Word、代码、结果、图表、复现清单、AI 使用记录和压缩包后，运行：

```powershell
python "<SKILL_ROOT>/scripts/validate_submission.py" "<PROJECT_ROOT>" --paper "submission/<官方论文文件>" --support "submission/<官方支撑材料文件>"
```

只有以下条件同时满足才可宣布完成：

- 当届规则、匿名、页数、文件类型、文件大小和 AI 披露均通过；
- M1/P1/P2/W1/W2 与受影响复验均为 PASS；
- 论文数字、图表、公式、代码结果和支撑材料一致；
- 15 专家恰好 15 份有效评分，平均分不低于 92，且无致命阻断项；
- 最终文件在最后一次门禁后未再发生实质变化。

最终回复列出产物链接、实际读取的入口、实际运行的关键命令和退出码、规则来源、核心模型和验证结论、专家平均分与轮次、Subagent 门禁状态、仍存在的限制和阻塞。不要把内部评分写成官方分数或奖项承诺。
