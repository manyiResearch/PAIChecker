# PAIChecker

PAIChecker detects semantic misalignment between a GitHub issue and the pull request intended to address it. Its multi-stage workflow runs specialized issue, PR-scope, and PR-connection analyzers, synthesizes their evidence in a coordinator, and validates the proposed labels against the code and test patches.

## Labels

- **IS (Incomplete Specification):** The issue scope or exact requirement evolved in discussion before the PR was merged, and the PR follows the sanctioned later details.
- **SC (PR Scope Creep):** The PR claims or implements additional scope beyond the target issue.
- **UL (Unspecified Literal Implementation):** The patch introduces a fixed runtime literal not specified in the issue, and the test patch explicitly asserts that same literal.
- **DP (Defective PR):** The current PR is an earlier buggy or incomplete change that later required a confirmed corrective or supplementary change.
- **FP (Follow-up PR):** The current PR is a later corrective or supplementary change in the same issue and PR chain.
- **Others:** Clear semantic misalignment exists, but it does not fit IS, SC, UL, DP, or FP.
- **No Misalignment:** The issue and PR align. This label is mutually exclusive with every other label.

Multiple misalignment labels may apply to one record. `No Misalignment` may appear only by itself.

## Installation

PAIChecker requires Python 3.13 or later.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Model and GitHub configuration

PAIChecker uses [LiteLLM](https://docs.litellm.ai/) and accepts any model name supported by the installed LiteLLM version. Pass the model with `--model` or set the compatible `MSWEA_MODEL_NAME` environment variable. Configure authentication with the environment variables required by the selected LiteLLM provider, for example:

```bash
export OPENAI_API_KEY="..."
export MSWEA_MODEL_NAME="openai/gpt-5.1"
```

For an OpenAI-compatible endpoint, LiteLLM also supports provider-specific base URL configuration such as `OPENAI_API_BASE` or model kwargs supported by LiteLLM. Consult the LiteLLM documentation for the provider and model you select.

The analyzers may use GitHub's REST API to verify linked issues and PRs:

```bash
export GITHUB_TOKEN="..."
```

Use a token with the minimum read-only permissions needed for the public or private repositories being analyzed. Other compatible runtime controls include:

- `MSWEA_MODEL_API_KEY`: pass an API key through the model factory.
- `MSWEA_MODEL_RETRY_STOP_AFTER_ATTEMPT`: set the maximum LiteLLM retry attempts; the default is `5`.
- `MSWEA_MODEL_CALL_INTERVAL`: add a delay in seconds between model calls.
- `MSWEA_COST_TRACKING=ignore_errors`: continue when LiteLLM cannot calculate model cost.
- `MSWEA_GLOBAL_COST_LIMIT` and `MSWEA_GLOBAL_CALL_LIMIT`: set optional process-wide limits.

## Command-line usage

Run one zero-based line index from a JSONL input file:

```bash
python -m paichecker.run.multi_swe_detector \
  --input examples/dp_example.jsonl \
  --index 0 \
  --model openai/gpt-5.1 \
  --output multi_swe_detector_outputs.jsonl \
  --output-dir data/sub_agent_outputs
```

Available options:

- `--input`: input JSONL path; required.
- `--index`: zero-based line index; default `0`.
- `--model`: LiteLLM model name; defaults to `MSWEA_MODEL_NAME`.
- `--output`: append-only result JSONL path; default `multi_swe_detector_outputs.jsonl`.
- `--output-dir`: sub-agent evidence cache directory; default `data/sub_agent_outputs`.
- `--include-assistant-messages`: include assistant message traces in the result; default disabled.

If the output already contains the selected `instance_id`, PAIChecker skips that record. Sub-agent stage outputs are cached under a model-specific directory and support partial recovery and fallback when a later stage cannot finish.

## Input format

Each line must be one JSON object with these fields:

| Field                  | Expected value                                   |
| ---------------------- | ------------------------------------------------ |
| `instance_id`        | String ending in`-<PR number>`                 |
| `issue_number`       | Issue number or list of issue numbers            |
| `problem_statement`  | Original issue description                       |
| `hints_text`         | Issue discussion or supplementary context        |
| `is_issue_mentioned` | Known PRs or artifacts associated with the issue |
| `pr_description`     | Pull request description                         |
| `pr_comments`        | Pull request discussion                          |
| `commit_message`     | Commit message or messages                       |
| `review_comments`    | Review discussion                                |
| `is_pr_mentioned`    | Issues or PRs that mention the current PR        |
| `patch`              | Production-code patch text                       |
| `test_patch`         | Test patch text                                  |
| `files`              | Changed-file metadata and related evidence       |

[`examples/dp_example.jsonl`](examples/dp_example.jsonl) contains one complete input record. It contains real public GitHub evidence and does not include its human label.

## Output format

Each run appends one JSON object containing `instance_id`, `status`, `final_output`, parsed `classifications`, model-call and token counts, pricing estimates, and cost estimates. Skipped runs also include `skip_reason`. With `--include-assistant-messages`, the record includes the assistant trace.

`final_output` uses one XML block per selected label:

```xml
<classification>
<label>DP</label>
<reason>Evidence-based final reason.</reason>
</classification>
```

The `classifications` array contains the same labels and reasons as parsed JSON objects. Multiple XML blocks may be emitted, except that `No Misalignment` is exclusive.

## Claude Code and Codex skills

This repository includes equivalent direct-analysis skills for Claude Code and Codex:

- Claude Code: `.claude/skills/paichecker/SKILL.md`
- Codex: `.agents/skills/paichecker/SKILL.md`

Ask the assistant to use the PAIChecker skill and provide the issue description, issue discussion, PR description and discussion, commit and review context, patch, test patch, and known cross-references. The skills analyze the supplied evidence directly and use read-only GitHub retrieval to complete relevant missing evidence; they do not invoke the Python CLI or modify GitHub. They do not invent facts or emit labels that cannot be supported, and their final response consists only of the same `<classification>` XML blocks used by the CLI.

## Security warning

**PAIChecker executes shell commands generated by language models on the local machine.** These commands may include `curl` requests and are not inherently safe. Run PAIChecker only in a disposable, isolated environment with restricted filesystem and network access. Do not run it on a machine or account containing sensitive data.

Use a minimally scoped, read-only `GITHUB_TOKEN`. Never expose write-capable credentials to the model or execution environment. Model calls can transmit supplied evidence to the configured provider and may incur charges.

## License

PAIChecker is released under the MIT License. See [`LICENSE`](LICENSE).
