<div align="center">

<h1>PAIChecker</h1>

**发现并检测 SWE-Bench 类基准中的 PR-Issue 语义错位**

[English](README.md) | [简体中文](README.zh-CN.md)

[![Paper](https://img.shields.io/badge/Paper-ASE%202026-blue)](https://doi.org/10.1145/3832783.3837557)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)

</div>

PAIChecker 通过特定模式文本分析、跨智能体结果综合和代码级验证，检测并分类 GitHub issue 与其关联 pull request 之间的语义错位。

## 动态

- **2026-08** — 🔥 Codex 和 Claude Code Skill 正式发布，并作为日常分类任务中运行完整 PAIChecker 的推荐轻量替代方案。Skill 使用相同的分类体系和 JSONL 记录结构，并写入兼容的核心分类字段。
- **2026-08** — 🔥 PAIChecker 及其标注数据集正式开源！
- **2026-07** — 🔥 PAIChecker 被 ASE 2026 录用！

## 语义错位类型

PAIChecker 严格遵循论文定义的五类模式：

| 标签 | 模式 | 定义 |
| --- | --- | --- |
| `SC` | PR Scope Creep | PR 实现了原始 issue 未要求的额外功能。 |
| `DP` | Defective PR | 当前 PR 引入了新 bug 或仅提供不完整修复，因而需要后续纠正。 |
| `FP` | Follow-up PR | 当前 PR 是对同一 issue 的先前 PR 的补充或纠正。 |
| `IS` | Incomplete Specification | 原始 issue 在后续讨论中被补充或修改，且 PR 实现了这些后续需求。 |
| `UL` | Unspecified Literal | PR 引入了测试会精确断言的固定运行时 literal，但 issue 及其讨论从未规定该 literal。 |

`Others` 表示不属于上述五类的明确错位。`No Misalignment` 仅在没有受证据支持的错位时使用，且不能与其他标签共存。

## 如何使用

### ⚙️ 方式一：使用 Skill

Skill 是日常分类任务的推荐轻量方案。它使用相同的分类体系和 JSONL 记录结构，并写入兼容的核心分类字段，无需运行 Python pipeline。

```bash
git clone --depth 1 https://github.com/manyifire/PAIChecker.git

# Codex
mkdir -p ~/.agents/skills
cp -R PAIChecker/.agents/skills/paichecker ~/.agents/skills/paichecker

# Claude Code
mkdir -p ~/.claude/skills
cp -R PAIChecker/.claude/skills/paichecker ~/.claude/skills/paichecker
```

安装后，让 Codex 或 Claude Code 运行 Skill：

```text
使用 PAIChecker Skill 对 <INPUT_JSONL> 中索引为 <INDEX> 的记录进行分类，将结果追加到 <OUTPUT_JSONL>，并报告运行状态和输出路径。
```

`<INDEX>` 从 0 开始计数，省略时默认为 `0`。每条输入记录包含一个 PR 及其关联 issue 证据；必需字段参见[输入格式](docs/input-format.md)。

### 🤖 方式二：让 LLM 运行完整 PAIChecker Pipeline

PAIChecker 按照上述分类体系识别 PR 与 issue 之间的语义错位类型。

当需要显式选择 LiteLLM 模型、多智能体执行过程、子智能体产物、超时/错误记录，或模型调用次数、token、定价、成本及可选 assistant message 等遥测信息时，请使用完整 runner。

```text
按照 https://github.com/manyifire/PAIChecker 中的“方式三：手动配置完整 PAIChecker”操作。在隔离环境中使用 <MODEL> 对 <INPUT_JSONL> 中索引为 <INDEX> 的记录运行 PAIChecker，将分类结果保存到 <OUTPUT_JSONL>，并报告运行状态。使用环境变量中已有的凭据；如果缺少凭据，请在运行前告诉我需要设置哪些环境变量。
```

### 🙌 方式三：手动配置完整 PAIChecker

<div align="center">
  <img src="docs/assets/paichecker-workflow.png" alt="PAIChecker 三阶段工作流" width="900">
</div>

需要 Python 3.13+，并支持 [LiteLLM](https://docs.litellm.ai/) 提供的任意模型。

```bash
git clone https://github.com/manyifire/PAIChecker.git
cd PAIChecker
conda create -n paichecker python=3.13
conda activate paichecker
python -m pip install -r requirements.txt

export OPENAI_API_KEY="..."
export MSWEA_MODEL_NAME="openai/<model>"
export GITHUB_TOKEN="..."  # 可选；请使用只读 token。

python src/run/paichecker.py \
  --input examples/dp_example.jsonl \
  --index 0 \
  --output results.jsonl
```

该命令会对 `--index` 指定的记录（从 0 开始计数）进行分类，并写入具有证据支持的 `classifications`。使用 `--model` 覆盖默认模型。输入格式参见[示例](examples/dp_example.jsonl)和[文档](docs/input-format.md)。

> [!WARNING]
> 完整 pipeline 会执行语言模型生成的 shell 命令。请仅在权限受限的隔离环境中运行，并且不要暴露具有写权限的凭据。

## 引用

如果 PAIChecker 对你的工作有帮助，请引用：

```bibtex
@article{wang2026paichecker,
  title={PAIChecker: Uncovering and Checking PR-Issue Misalignment in SWE-Bench-Like Benchmarks},
  author={Wang, Manyi and Xu, Junjielong and He, Pinjia},
  journal={arXiv preprint arXiv:2607.28587},
  year={2026}
}
```

## 致谢

PAIChecker 基于 [Mini-SWE-Agent](https://github.com/SWE-agent/mini-swe-agent) 构建。
