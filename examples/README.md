# 端到端示例：产物布局与状态流转

本目录说明一次完整运行（CUMCM，3 天赛程，`championship` 模式）在 `PROJECT_ROOT` 中应留下的产物形态。示例文件为占位说明，不是可运行数据。

## 运行命令序列

```powershell
# 1. 初始化（Agent 自动执行）
python "<SKILL_ROOT>/scripts/init_project.py" "<PROJECT_ROOT>" --competition "CUMCM" --year "2026"
python "<SKILL_ROOT>/scripts/doctor.py" --project "<PROJECT_ROOT>"

# 2. 阶段推进（Agent 按路由表读取各角色 SKILL.md 后执行）
#    Stage 2-4  → references/roles/建模手
#    Stage 5-7  → references/roles/编程手（P1 通过后才全量计算）
#    Stage 8-9  → references/roles/论文手（W1 通过后才写长文）

# 3. 冻结与专家评审
python "<SKILL_ROOT>/scripts/aggregate_panel.py" --input "review/panel_round_1.json" --output "state/panel_latest.json" --threshold 92

# 4. 最终门禁
python "<SKILL_ROOT>/scripts/validate_submission.py" "<PROJECT_ROOT>" --paper "submission/579_参赛论文.pdf" --support "submission/579_支撑材料.zip"
```

## 期望的项目布局

```
PROJECT_ROOT/
├── state/
│   ├── decision_log.json        # 唯一状态源：阶段、门禁、模式、事件
│   ├── panel_latest.json        # 最近一轮 15 专家聚合结果
│   └── submission_check.json    # validate_submission.py 输出
├── 题目分析报告.md               # 建模手交付物
├── 术语表格.md                   # 建模手交付物
├── code/                        # 权威 Python/MATLAB 代码
├── results/
│   ├── *.csv                    # 真实运行结果表
│   └── 复现清单.json             # 种子/哈希/依赖/唯一复现命令
├── figures/
│   ├── raw_q1_*.png             # 原始数据图（每问每类 ≥1）
│   ├── process_q1_*.png         # 模型过程图
│   └── result_q1_*.png          # 最终结果图
├── checkpoints/
│   └── v1/                      # Checkpoint V1：首次完整可提交版本快照
├── review/
│   └── panel_round_1.json       # 15 份独立评分（含证据与独立性确认）
├── submission/
│   ├── 579_参赛论文.pdf          # 非图片 PDF，无目录，无承诺书/编号页，正文 ≤30 页（全文按赛区口径 ≤51 页），≤20MB
│   ├── 579_支撑材料.zip          # 含可运行源码，路径安全
│   └── submission_manifest.json # 文件清单 + SHA-256 + page_report
└── 完整论文-LaTeX/               # 源码项目（.build.json 哈希绑定）
```

## 关键节点（对应 references/workflow.md 的 48 小时时间盒）

| 时间 | 里程碑 |
|---|---|
| 前 10% | 规则核验 + 题意冻结（Stage 0–1） |
| 前 25% | 数据边界 + M1 PASS（Stage 2–4） |
| 前 55% | P1 PASS + 主模型（Stage 5） |
| 前 70% | 全量验证 + P2 PASS（Stage 6–7） |
| 前 85% | W1 PASS + 正文（Stage 8） |
| 前 93% | W2 PASS + **Checkpoint V1** + 提交包（Stage 9–10） |
| 最后 7% | 15 专家 panel、定向返工、上传复核 |

单阶段任务（如只要论文）只运行对应阶段与门禁，不强制完整流程；时间不足按 `references/运行模式.md` 降档。
