# Feature request — FILED at https://github.com/apache/airflow/issues/68845

**Title:** Add SandboxExecutor: run each task in an ephemeral cloud sandbox (Daytona/E2B/Modal/islo)

---

### Description

A new executor that runs each Airflow task instance in an ephemeral, isolated
cloud **sandbox** via pluggable backends (a local subprocess reference backend
plus Daytona, E2B, Modal, islo). It implements `BaseExecutor` and requires **no
core changes** (per AIP-51, which made the executor interface public and
third-party executors first-class). Topology follows the Airflow 3 EdgeExecutor
+ Task SDK model: the in-sandbox Task SDK supervisor heartbeats and ships logs
to the api-server, and the executor only reconciles terminal exit state from a
polling watcher. Intended to ship as a provider / third-party package.

A working reference implementation already exists:
https://github.com/zozo123/airflow-provider-sandbox

### Use case / motivation

Teams increasingly want **strong per-task isolation** and a **serverless /
ephemeral execution model** without operating Celery or Kubernetes:

- running untrusted or AI-generated code with a fresh, disposable environment
  per task;
- per-task dependency/image isolation without a shared worker image;
- bursty, heavyweight, isolation-sensitive jobs (ML training, data extraction)
  that benefit from a clean microVM/container each run.

No existing executor targets ephemeral cloud sandboxes: Local/Celery use
long-lived workers; Kubernetes needs a cluster; ECS/Batch are AWS-specific and
container-orchestration-shaped; Edge targets a self-hosted worker protocol. A
provider-backed `SandboxExecutor` fills this gap while staying vendor-neutral
(the local backend needs no SaaS account).

### Related issues / prior art

- AIP-51 (executor decoupling — `BaseExecutor` is the public interface)
- Precedent: AWS Batch / ECS executors shipped as provider code
- `crabbox` (provider-abstraction inspiration): https://github.com/openclaw/crabbox
- `[DISCUSS]` devlist thread: _link once sent_

### Are you willing to submit a PR?

- [x] Yes I am willing to submit a PR!

### Code of Conduct

- [x] I agree to follow this project's Code of Conduct

---

_Created with assistance from Claude (Anthropic); all code reviewed by a human
maintainer._
