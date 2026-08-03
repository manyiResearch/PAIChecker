# PAIChecker Input Format

PAIChecker reads UTF-8 JSONL: each non-empty line is one self-contained PR-Issue record. See [`examples/dp_example.jsonl`](../examples/dp_example.jsonl) for a complete record.

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `instance_id` | string | Stable identifier ending in `-<PR number>`, such as `owner__repo-123`. |
| `issue_number` | string or array of strings | Linked issue number or numbers. Multiple linked issues belong to the same record and are analyzed together. |
| `problem_statement` | string | Original issue description used as the task specification. For multiple issues, include all issue descriptions with their identifiers and boundaries preserved. |
| `hints_text` | string | Issue discussion and supplementary issue-side context available before the PR was merged. |
| `is_issue_mentioned` | array | Known PRs and issues associated with each linked issue, including number, state, URL, and relationship evidence when available. |
| `pr_description` | string | PR title, body, and claimed scope. |
| `pr_comments` | array | PR discussion in chronological order. |
| `commit_message` | string or array of strings | Commit message or messages for the current PR. |
| `review_comments` | array | Review discussion for the current PR. |
| `is_pr_mentioned` | object | Issues and PRs that mention the current PR. |
| `patch` | string | Production-code patch. |
| `test_patch` | string | Test patch. |
| `files` | array | Changed-file metadata and any additional patch or raw-file evidence. |

## Requirements

- Include every field in each record. Use an empty string, array, or object when an artifact is known to be empty; do not omit its key.
- Preserve exact GitHub text, chronology, merge state, identifiers, and URLs. Do not summarize away evidence needed to establish scope or PR relationships.
- Store all issues linked to one PR in the same record. Keep issue identifiers attached to their descriptions, discussions, and cross-references.
- Keep `patch` and `test_patch` separate so PAIChecker can validate implementation and test-oracle evidence independently.
- Do not include human labels in evaluation inputs.
