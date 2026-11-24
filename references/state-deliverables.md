# 状态、目录与交付物

## 项目目录

```text
PROJECT_ROOT/
├─ input/                 只读副本或输入清单
├─ analysis/              题目分析、数据合同、符号与模型设计
├─ src/                   权威代码
├─ results/               表格、日志、模型文件、复现清单
├─ figures/               正式图与审阅预览
├─ paper/                 Word/LaTeX/PDF 及章节源文件
├─ support_materials/     准备压缩的代码、说明和 AI 披露
├─ submission/            最终提交文件与清单
├─ review/                独立门禁和 panel 轮次
└─ state/                 decision_log.json、panel_latest.json
```

输入附件只读。所有自动生成物都应可从 `src/`、输入哈希和唯一复现命令重建。

## 状态字段

`decision_log.json` 至少记录：竞赛、届次、题号、截止时间、当前阶段、规则来源、数据台账、实验单位、外部数据决定、模型决定与拒绝方案、验证设计、门禁状态、产物路径与哈希、AI 使用、panel 历史和最终 verdict。

样例中的 `null` 是待填字段，不得作为已验证结果。只有实际运行可写 `PASS`、`true` 或分数。

## 最终交付清单

- 官方要求格式的匿名论文及需要时的源文件；
- 可运行的 Python/MATLAB 代码、环境说明和唯一复现命令；
- 原始、中间和最终结果表，关键结果与论文一致；
- 正式图表及适用时的可编辑矢量版本；
- `results/reproducibility_manifest.json`：种子、输入 SHA-256、参数、环境、命令、运行时间和关键结果；
- `submission/submission_manifest.json`：文件、实际字节数、SHA-256、联合 `artifact_bundle_sha256`、官方限制核对和人工复核者；联合哈希由按路径排序的每个交付文件 `path + sha256` 计算，供 panel 绑定冻结版本；
- 官方要求的 AI 使用详情、报告、引用或无 AI 声明；
- 支撑材料 ZIP/RAR，内部路径安全、无密钥和个人身份；
- `state/panel_latest.json` 与历史评分轮次。

不要把临时缓存、虚拟环境、个人路径、API 密钥、未脱敏元数据、与论文不一致的旧结果或无关大文件放入提交包。
