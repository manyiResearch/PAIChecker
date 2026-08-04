<div align="center">

<h1>PAIChecker</h1>

**Uncovering and Checking PR-Issue Misalignment in SWE-Bench-Like Benchmarks**

[English](README.md) | [简体中文](README.zh-CN.md)

[![Paper](https://img.shields.io/badge/Paper-ASE%202026-blue)](https://doi.org/10.1145/3832783.3837557)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)

</div>

PAIChecker detects and classifies semantic misalignment between a GitHub issue and its linked pull request through pattern-specific text analysis, cross-agent synthesis, and code-level validation.

## News

- **2026-08** — 🔥 The Codex and Claude Code Skills are available as the recommended lightweight replacement for routine full-PAIChecker classification runs. They use the same taxonomy and JSONL record schema and write compatible core classification fields.
- **2026-08** — 🔥 PAIChecker and its annotated datasets are publicly available!
- **2026-07** — 🔥 PAIChecker was accepted by ASE 2026!

## Misalignment Types

PAIChecker follows the five-pattern taxonomy defined in our paper:

| Label | Pattern | Definition |
| --- | --- | --- |
| `SC` | PR Scope Creep | The PR delivers functionality beyond what the original issue requests. |
| `DP` | Defective PR | The current PR introduces a bug or provides an incomplete fix that requires a later correction. |
| `FP` | Follow-up PR | The current PR supplements or corrects an earlier PR for the same issue. |
| `IS` | Incomplete Specification | The original issue is supplemented or revised in later discussion, and the PR implements those later requirements. |
| `UL` | Unspecified Literal | The PR introduces a fixed runtime literal that the tests assert exactly, but the issue and its discussion never specify. |

`Others` denotes clear misalignment outside these five patterns. `No Misalignment` is exclusive and is used only when no misalignment is supported.

## How to Use

### 👉 Option 1 - Prompt Your LLM

PAIChecker classifies PR-issue misalignment using the taxonomy described above.

**Option 1 — Use the Skill (fastest)**

The Skill is the recommended lightweight replacement for routine classification. It applies the same taxonomy to the same JSONL record schema and writes the compatible core fields `instance_id`, `status`, `final_output`, and `classifications`, without running the Python pipeline.

```text
Install the PAIChecker Skill from https://github.com/manyifire/PAIChecker. Use it to classify record <INDEX> from <INPUT_JSONL>, append the result to <OUTPUT_JSONL>, and report the run status and output path.
```

`<INDEX>` is zero-based and defaults to `0` when omitted. The input format is shared with the full PAIChecker; each record contains one PR and its linked issue evidence.

**Option 2 — Run the full PAIChecker (reference pipeline)**

Use the full runner when you need its explicit LiteLLM model selection, multi-agent execution, sub-agent artifacts, timeout/error records, or model-call, token, pricing, cost, and optional assistant-message telemetry. These runner-specific fields and artifacts are intentionally not fabricated by the Skill, so the two paths are core-result compatible rather than byte-for-byte equivalent.

```text
Follow the "Manual Setup → Run the full PAIChecker" instructions at https://github.com/manyifire/PAIChecker. In an isolated environment, run PAIChecker on record <INDEX> of <INPUT_JSONL> with <MODEL>, save its classifications to <OUTPUT_JSONL>, and report the run status. Use credentials already configured in environment variables; if any are missing, tell me which variables to set before running.
```

### 🙌 Option 2 - Manual Setup

Option 1 — Use the Skill (recommended)

The Skill is the lightweight replacement for routine classification. It uses the same taxonomy and JSONL record schema and writes compatible core classification fields without running the Python pipeline.

```bash
git clone --depth 1 https://github.com/manyifire/PAIChecker.git

# Codex
mkdir -p ~/.agents/skills
cp -R PAIChecker/.agents/skills/paichecker ~/.agents/skills/paichecker

# Claude Code
mkdir -p ~/.claude/skills
cp -R PAIChecker/.claude/skills/paichecker ~/.claude/skills/paichecker
```

Option 2 — Run the full PAIChecker (reference pipeline)

<div align="center">
  <img src="docs/assets/paichecker-workflow.png" alt="PAIChecker three-phase workflow" width="900">
</div>

Requires Python 3.13+, `bash`, `curl`, and any model supported by [LiteLLM](https://docs.litellm.ai/).

```bash
git clone https://github.com/manyifire/PAIChecker.git
cd PAIChecker
conda create -n paichecker python=3.13
conda activate paichecker
python -m pip install -r requirements.txt

export OPENAI_API_KEY="..."
export MSWEA_MODEL_NAME="openai/<model>"
export GITHUB_TOKEN="..."  # Optional; use a read-only token.

python src/run/paichecker.py \
  --input examples/dp_example.jsonl \
  --index 0 \
  --output results.jsonl
```

The command classifies the record selected by the zero-based `--index` and writes evidence-backed `classifications`. Use `--model` to override the default model. See the [example](examples/dp_example.jsonl) and [input format](docs/input-format.md).

> [!WARNING]
> The full pipeline executes shell commands generated by language models. Run it only in an isolated environment with restricted permissions and never expose write-capable credentials.

## Citation

If PAIChecker helps your work, please cite:

```bibtex
@article{wang2026paichecker,
  title={PAIChecker: Uncovering and Checking PR-Issue Misalignment in SWE-Bench-Like Benchmarks},
  author={Wang, Manyi and Xu, Junjielong and He, Pinjia},
  journal={arXiv preprint arXiv:2607.28587},
  year={2026}
}
```

## Acknowledgements

PAIChecker is built on [Mini-SWE-Agent](https://github.com/SWE-agent/mini-swe-agent).
