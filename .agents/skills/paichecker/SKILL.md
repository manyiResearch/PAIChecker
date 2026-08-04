---
name: paichecker
description: Detect or classify semantic misalignment between a GitHub pull request and its linked issue or issues. Use for binary detection or SC, FP, DP, IS, UL, Others, and No Misalignment classification from PR or issue identifiers, URLs, supplied artifacts, and read-only GitHub evidence.
---

# PAIChecker

Analyze the supplied issue-PR pair directly. Do not invoke the PAIChecker Python CLI. Use read-only GitHub retrieval to complete the evidence when the supplied material is insufficient. Never invent facts, merge states, chronology, causal links, or missing content.

## Inputs and modes

Require a PR in one of these forms:

- `owner/repo#123`
- `https://github.com/owner/repo/pull/123`
- A supplied PAIChecker record containing an `instance_id` that identifies the repository and PR

An explicit issue is optional and may be `owner/repo#45`, an issue URL, or the issue fields in a supplied record. A bare number such as `#123` is insufficient unless the repository is unambiguous from another supplied identifier.

Support two modes:

- `binary`: decide whether any semantic misalignment exists.
- `types`: return every independently supported PAIChecker classification. Use this mode when the user does not specify a mode.

When no issue is supplied, inspect the PR body, closing keywords, timeline, and cross-references to find every issue explicitly linked to the PR. If none exists, stop and return the `no_linked_issue` JSON object defined in Final output. If several issues are linked, keep them in one evidence set and analyze the PR against their combined issue-side context; do not emit separate results per issue.

## Evidence policy

Treat textual evidence as primary:

- Issue description and discussion
- PR description and comments
- Commit messages and review comments
- Timeline and cross-reference text
- Later or earlier related issue and PR text

Use `patch`, `test_patch`, changed-file metadata, and raw source files as secondary confirmation or disambiguation. Do not originate a text-dependent label from diff size, filenames, or code alone. Ignore documentation, comments, formatting, `.gitignore`, `.rst`, and other non-functional-only differences unless the evidence demonstrates functional or test behavior impact.

Quote or cite the concrete input field or GitHub artifact supporting every selected label. Prefer stronger and more direct textual evidence when sources conflict. Prefer retrieved GitHub evidence over stale or incomplete hint data.

## Evidence collection

Start with all supplied evidence. Normalize the PR and every issue to `owner/repo#number`. Derive the repository, issue number or numbers, and current PR number from explicit identifiers, URLs, or `instance_id`; do not guess a repository from a bare number.

When evidence is incomplete, retrieve only read-only GitHub material relevant to the unresolved judgment:

1. Inspect the target issue body, comments, and timeline for baseline scope, later supplementation, linked PRs, and explicit failure reports.
2. Inspect the current PR body, comments, reviews, commits, merge state, and changed files for claimed scope and implementation evidence.
3. Inspect referenced issues and PRs when their relationship may establish SC, DP, or FP.
4. Fetch raw changed files only when the supplied patch lacks enough context to validate a candidate label.
5. Do not modify issues, PRs, comments, labels, branches, or repository content.

For DP and FP, construct candidates before retrieving details:

- Current PR number: parse the numeric suffix of `instance_id` or use the supplied PR number.
- DP candidates: merged PRs in `is_pr_mentioned`, plus merged PRs in `is_issue_mentioned` with a number greater than the current PR number. Include closed issues that explicitly discuss the current PR as a defect source.
- FP candidates: merged PRs in `is_issue_mentioned` with a number lower than the current PR number.
- Exclude the current PR from both sets.
- If both sets are empty, conclude that DP and FP are unsupported without broad searching.
- With multiple issue numbers, identify the target issue matching the issue description and evaluate each issue relationship independently. Retrieve candidate details needed to disambiguate mixed hint data.
- Inspect only candidate PRs and directly relevant linked artifacts. Do not treat a bare cross-reference as a causal or corrective relationship.

## Classification workflow

Evaluate labels in this order, retaining every independently supported misalignment label:

1. IS: compare the original issue baseline with pre-merge discussion.
2. SC: compare the issue-description baseline with PR-side scope claims.
3. UL: compare each asserted literal across issue text, production patch, and test patch.
4. DP: determine whether the current PR is the earlier defective or incomplete change.
5. FP: determine whether the current PR is the later same-issue corrective or supplementary change.
6. Others: consider only a clear textual mismatch not covered by the named labels.
7. Validate candidates against code and tests.
8. Use No Misalignment only when every misalignment label is unsupported or dropped.

## IS: Incomplete Specification

Classify IS when the issue scope or exact requirement evolved before merge and the PR follows the sanctioned later details. Match at least one condition:

1. A maintainer explicitly requests missing information or clarification, and the reporter supplies it. A maintainer supplementing their own issue does not qualify under this condition.
2. The reporter proactively adds reproduction code or steps, actual behavior, expected behavior, or a meaning-changing correction to the original issue.
3. Discussion adds a new distinct problem, failing case, edge case, or expected behavior that was absent from the baseline.
4. The baseline leaves a required interface, name, format, or behavior undecided, and discussion explicitly finalizes what the PR must implement.

Distinguish what to solve from how to solve it. Root-cause analysis, implementation notes, coding approaches, acknowledgments, prioritization, and context-only explanations are not IS. Reproducing or rephrasing an already stated failure without adding a new constraint is not IS. Selecting among solutions already prescribed in the original issue is ordinarily refinement, not scope evolution.

Examples and boundaries:

- A maintainer requests a complete reproduction script and the reporter provides it: IS.
- Discussion reveals that a related sparse variant still fails after the dense case described initially: IS if the PR implements that added case.
- An issue asks what name or format to use and discussion establishes the required answer: IS.
- A maintainer merely explains the likely implementation or restates the mismatch: not IS.

## SC: PR Scope Creep

Use the original issue description as the requested-scope baseline. Discussion can reveal an additional problem but does not automatically broaden that baseline for SC.

Classify SC when at least one condition holds:

1. PR description or commits explicitly close or fix multiple distinct issues beyond the target issue.
2. PR-side text claims an unrelated functionality change, bug fix, enhancement, refactor with behavioral scope, or additional case not requested by the issue.
3. Commit messages or review context explicitly connect added work or tests to another issue outside the baseline.
4. Discussion introduces a distinct additional problem and PR-side text claims delivery of both the baseline and added problem.
5. `issue_number` contains multiple target issue numbers; preserve the existing PAIChecker multi-issue quick-check interpretation and classify SC, citing the multiple issue scopes.

Do not classify SC from a long or broad-looking diff alone. Do not count implementation details necessary to solve the baseline. Do not count unrelated-looking tests without matching production behavior and PR-side textual scope evidence. Do not count non-functional-only additions.

Examples and boundaries:

- A PR says it closes three issues while the supplied issue describes one bug: SC.
- A PR fixes the requested behavior and explicitly claims a separate autodoc fix: SC.
- A commit says `Fixed #A` and `Refs #B` while adding assertions for #B: SC when #B is outside the baseline.
- A large patch or many tests implementing only the requested behavior: not SC.

## UL: Unspecified Literal Implementation

Classify UL only when all conditions hold for the same functionally relevant literal:

1. `patch` newly introduces or defines the literal as a fixed runtime constant.
2. `test_patch` explicitly asserts that exact literal.
3. The exact literal does not appear in the issue description or discussion. Require exact string matching; a paraphrase does not specify the literal.

Inspect strings, numbers, exact output, and exception messages. Do not count a literal found only in the patch or only in tests. Do not count a value forwarded from configuration, arguments, external data, or existing code. Do not count metadata such as `__name__` or `__doc__` when the patch merely exposes an existing value. Do not count comments or documentation literals.

Examples and boundaries:

- The patch adds a fixed exception message and the test asserts that exact message, while the issue never states it: UL.
- A test supplies `42` through configuration and the patch propagates it: not UL.
- A wrapper exposes an existing function name or docstring and tests its existing value: not UL.

## DP: Defective PR

Classify DP when the current PR is the earlier problematic or incomplete change and at least one condition holds:

1. After merge, a later issue or PR explicitly and non-speculatively states that the current PR introduced a bug or regression, and a merged correction exists. The correction may belong to a different issue.
2. A later merged PR functionally supplies behavior missing from the current PR and adds or updates regression tests. Patch-only follow-ups without tests do not qualify.
3. The same issue has multiple PRs, explicit discussion says the current earlier PR failed, was incomplete, or introduced a regression, and a later corrective PR merged. The later PR description may be terse when the issue discussion supplies the explicit causal evidence.

For every candidate artifact, classify the mention as: regression introduced by this PR, incomplete prior fix, or unrelated reference. Only the first two support DP. Reject speculative wording such as `probably`, `maybe`, or `might`; bare mentions; chronology without causal or incomplete-fix evidence; unmerged corrections; and non-functional-only follow-ups.

## FP: Follow-up PR

Classify FP only when all conditions hold:

1. An earlier merged PR attempted to address the exact same target issue.
2. The current PR is a later functional supplement, completion, or correction in that same issue chain.
3. Evidence connects the current PR to the shortcoming, partial fix, or regression from the earlier PR.

An earlier PR that fixed the issue but introduced a new bug can still support FP when the current PR fixes that bug in the same issue chain. Do not count an older PR that merely cross-references the issue, work re-filed under a different issue chain, the first or only merged PR for the target issue, or a non-functional-only follow-up.

For records with multiple issue numbers, default to no FP if any target issue has the current PR as its only merged PR, unless PR-side text explicitly describes the current PR as a follow-up, supplement, completion, or continuation. Identify the primary target issue from the issue description before applying same-issue chronology.

DP and FP describe opposite positions in a correction chain: DP is the earlier defective PR; FP is the later corrective PR. They may coexist only when independent evidence places the current PR in both roles across valid chains.

## Others and No Misalignment

Classify Others only when clear abnormal textual evidence establishes a real issue-PR misalignment that does not fit IS, SC, UL, DP, or FP. Do not use Others for uncertainty, missing evidence, pure refactoring, documentation changes, or a suspicious-looking diff.

Classify No Misalignment only when no other label remains. It is mutually exclusive with every other label.

## Code validation

After deriving text-supported candidates, validate each against `patch`, `test_patch`, `files`, and any necessary raw file context:

- SC: retain when code confirms the extra claimed scope; drop when all functional changes stay within the baseline.
- IS: retain when implementation or tests cover the requirement or edge case added in discussion; drop when they cover only the original baseline.
- UL: retain only when the exact literal triad is satisfied; otherwise drop.
- DP and FP: retain when code is consistent with the documented correction chain; drop only when code directly contradicts the textual claim.
- Others: retain when functional evidence matches the stated textual anomaly.

Retain a candidate when code is ambiguous but textual evidence is strong. Drop it when code directly contradicts the claim. Do not create a new label solely during code validation. If every candidate is dropped, use No Misalignment.

## Final output

Return exactly one valid JSON object and no Markdown or surrounding text. Emit each selected label at most once. Reasons must quote or cite concrete evidence and explain why the definition is met.

For `binary` mode, consolidate the retained classifications into one decision:

```json
{
  "status": "ok",
  "pr": "owner/repo#123",
  "issues": ["owner/repo#45"],
  "misaligned": true,
  "reason": "Concise evidence-based explanation."
}
```

Set `misaligned` to `false` only when the classification workflow yields No Misalignment.

For `types` mode, return the retained classifications:

```json
{
  "status": "ok",
  "pr": "owner/repo#123",
  "issues": ["owner/repo#45"],
  "classifications": [
    {
      "label": "DP",
      "reason": "A later merged PR explicitly attributes the regression to the current PR and adds regression coverage for the correction."
    }
  ]
}
```

Use only these exact labels: `SC`, `FP`, `DP`, `IS`, `UL`, `Others`, `No Misalignment`. If no misalignment label is supported, return exactly one `No Misalignment` classification. Never combine `No Misalignment` with another label.

When a PR has no linked issue and no issue was supplied, return exactly:

```json
{
  "status": "no_linked_issue",
  "pr": "owner/repo#123",
  "issues": []
}
```
