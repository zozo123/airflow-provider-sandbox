# [DISCUSS] email — to dev@airflow.apache.org

**Subject:** [DISCUSS] SandboxExecutor — run each task in an ephemeral cloud sandbox (provider)

---

Hi all,

I'd like to propose a new executor, `SandboxExecutor`, that runs each task
instance in an ephemeral, isolated cloud **sandbox** behind a pluggable provider
layer (a local subprocess reference backend, plus Daytona / E2B / Modal / islo).

Motivation: strong per-task isolation and a serverless/ephemeral execution model
(untrusted or AI-generated code, per-task dependency isolation, bursty
heavyweight jobs) without operating Celery or Kubernetes. No existing executor
targets ephemeral cloud sandboxes.

Scope/impact: it implements the public `BaseExecutor` interface only — **no core
changes** (per AIP-51) — so I don't believe an AIP is required; please correct
me if you disagree. The Airflow 3 topology is EdgeExecutor-like: the in-sandbox
Task SDK supervisor heartbeats and ships logs to the api-server; the executor
reconciles terminal exit state via a polling watcher.

Working reference implementation (runs end-to-end on the local backend, unit
tests included): https://github.com/zozo123/airflow-provider-sandbox
Tracking issue: <link>

Two questions for the list:

1. Would you prefer this as a **community provider in the monorepo** or as a
   **third-party package**? Given the SaaS backends move fast and want
   independent release cadence, third-party may fit best — but I'm happy to
   pursue monorepo inclusion if there's interest.
2. If monorepo: are there **≥2 maintainers willing to be stewards** and **a
   committer willing to sponsor**? `ACCEPTING_PROVIDERS.rst` requires these plus
   a continuous system-test validation plan for the live SaaS backends, which I
   will provide.

Disclosure: the implementation was developed with assistance from Claude
(Anthropic); all code has been human-reviewed and I take full responsibility for
it.

Thanks,
zozo123
