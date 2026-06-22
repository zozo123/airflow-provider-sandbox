# PR body — use ONLY after devlist lazy-consensus clears

**Title:** `Add Sandbox provider with SandboxExecutor`

---

This adds a `Sandbox` provider whose `SandboxExecutor` runs each task instance in
an ephemeral cloud sandbox behind a pluggable provider layer (local subprocess
reference backend + Daytona, E2B, Modal, islo). It implements `BaseExecutor`
only — no core changes (AIP-51) — and follows the Airflow 3 Task SDK topology:
the in-sandbox supervisor heartbeats/ships logs to the api-server; the executor
reconciles terminal exit state from a polling watcher with a transient-error
threshold so a single failed poll never kills a healthy task.

- Provider abstraction (`SandboxProvider`) with capability flags per backend.
- `local` backend runs with zero credentials (powers the demo + unit tests).
- `remote_logging` is enforced at `start()`; `get_task_log` is a documented
  best-effort fallback.
- Adoption via deterministic, labelled sandbox names where the backend supports
  reattach.

closes: #ISSUE

### Tests

- Unit tests for the provider contract (`local`) and the watcher's
  transient-`UNKNOWN`-vs-`GONE` logic.
- System-test plan for live-SaaS backends (see `tests/system/`), with a
  continuous validation cadence per `ACCEPTING_PROVIDERS.rst`.

### Documentation

- Provider docs + example DAG + runnable `examples/demo.py`.

### Dependencies / licensing

- SaaS SDKs (`daytona`, `e2b`, `modal`, `islo`) are **optional extras** only;
  each vetted against the ASF 3rd-Party License Policy.

### AIP

- [x] No AIP needed — implements the public `BaseExecutor` interface only, no
  core/API/scheduler changes (AIP-51).

##### Was generative AI tooling used to co-author this PR?

- [x] Yes (please specify the tool below)

This PR was created with the assistance of **Claude (Anthropic)**. All generated
code was reviewed and understood by me; `prek run --from-ref main` and the tests
pass locally, and I take full responsibility for the contribution per the
Gen-AI guidelines.

<!-- Generated-by: Claude (Anthropic) -->
