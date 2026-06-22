# Upstreaming `SandboxExecutor` to Apache Airflow

The sanctioned sequence (per `providers/ACCEPTING_PROVIDERS.rst`, AIP-51, and
`contributing-docs/05_pull_requests.rst`). **Do not open a cold PR.**

## Current status

- ✅ Working reference implementation (this repo).
- ✅ Feature-request issue filed: https://github.com/apache/airflow/issues/68845
- ✅ PR-ready, monorepo-shaped branch staged as a draft on the fork:
  https://github.com/zozo123/airflow/pull/1 (base `zozo123:main`; retarget to
  `apache:main` only after the steps below).
- ⏳ Next (human-driven): `[DISCUSS]` email to dev@airflow, secure ≥2 stewards +
  1 committer sponsor, clear the 7-day lazy-consensus window.

## Go / no-go

- **AIP required?** No. AIP-51 made `BaseExecutor` the public, stable executor
  interface; third-party executors need no core changes. (AWS Batch/ECS
  executors shipped as ordinary provider PRs, no per-executor AIP.) An AIP is
  only needed if we add new core/API/scheduler/worker-protocol surface — we do
  not.
- **Monorepo or standalone?** Default **standalone third-party PyPI package**
  (this repo). Monorepo inclusion is gated on ≥2 stewards + ≥1 committer sponsor
  + continuous system-test plan, cleared via a 7-day devlist lazy-consensus. The
  `apache-airflow-providers-*` name is ASF-reserved — third-party packages must
  use their own name (`airflow-provider-sandbox`).

## Ordered steps

1. ✅ **Working reference implementation first** (this repo). Verify selection
   via `[core] executor = <fqcn>` and an end-to-end run on a backend.
2. **Open a `feature_request` issue** (`.github/ISSUE_TEMPLATE/2-feature_request.yml`).
   See [`proposals/ISSUE.md`](../proposals/ISSUE.md).
3. **Send a `[DISCUSS]` email** to dev@airflow.apache.org linking the issue +
   this repo; ask in-repo-vs-third-party and solicit stewards/sponsor. See
   [`proposals/DISCUSS_email.md`](../proposals/DISCUSS_email.md).
4. **Wait out the 7-day lazy-consensus window**; address objections.
5. **Only then**, if sponsor + steward commit → monorepo PR; otherwise publish
   the standalone package to PyPI. PR body: [`proposals/PR_BODY.md`](../proposals/PR_BODY.md).

## Hard requirements for any apache/airflow commit

- **DCO**: every commit `git commit -s` → `Signed-off-by:` (repo-level probot
  check is a hard merge gate). Author identity must match the trailer.
- **AI disclosure (mandatory)**: tick the PR template's
  `##### Was generative AI tooling used to co-author this PR?` and name the tool.
- **AI provenance (ASF)**: `Generated-by: Claude (Anthropic)` commit trailer.
- **Never** `Co-authored-by:` for the AI — AI is not a human/legal author.
- Imperative, no-prefix title: `Add Sandbox provider with SandboxExecutor`
  (not `feat: ...`, not `Fixes #NNNNN`).
- Tests + docs + (provider) CHANGELOG; vet every SaaS SDK against the ASF
  3rd-Party License Policy; no unrelated diff; ≤3 open PRs.

## Red flags that get a PR closed

Cold mega-PR · unreviewed AI-slop · missing Gen-AI disclosure · empty/template
body · unrelated changes · unsigned commits · conventional-commit prefixes ·
`Co-authored-by` for AI · squatting the apache namespace · claiming no-AIP while
touching core · no working impl · no system-test plan.
