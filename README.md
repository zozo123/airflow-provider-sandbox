# airflow-provider-sandbox

> Run each Apache Airflow task instance in an **ephemeral cloud sandbox** —
> behind a pluggable provider layer (local · Daytona · E2B · Modal · islo).

`SandboxExecutor` does for ephemeral sandboxes what `KubernetesExecutor` does
for pods: every queued task leases a fresh, isolated sandbox, runs the task
inside it, reports the exit state, and tears the sandbox down. The provider
abstraction is modelled on [crabbox](https://github.com/openclaw/crabbox)'s
"provision → sync → run → cleanup" contract, so one executor targets many
backends via a single config key — like `crabbox --provider`.

```
Scheduler ──workload──▶ SandboxExecutor ──▶ SandboxProvider ──▶ ephemeral sandbox
                              ▲                                   (task runs here)
                              └────── polling watcher ◀── exit code / state
```

## Why

- **Isolation by default** — untrusted code, per-task dependency stacks, ML jobs
  that shouldn't share a worker.
- **Vendor-neutral** — the same DAG runs on a local subprocess (zero setup) or
  on Daytona / E2B / Modal / islo by changing one line of config.
- **Airflow-3 native** — the in-sandbox Task SDK supervisor heartbeats and ships
  logs straight to the api-server; the executor only reconciles exit state. The
  api-server stays the single source of truth for task state.

## Install

```bash
pip install airflow-provider-sandbox            # local backend only
pip install 'airflow-provider-sandbox[daytona]' # + Daytona SDK
pip install 'airflow-provider-sandbox[e2b]'     # + E2B, [modal], [islo]
```

## Quickstart — 20-second demo, no credentials

```bash
python examples/demo.py          # runs a task in a local subprocess "sandbox"
SANDBOX_PROVIDER=daytona python examples/demo.py   # needs DAYTONA_API_KEY
```

It drives the exact lifecycle the executor uses
(`create → upload → run → poll → logs → destroy`) and prints each step.

## Configure

```ini
[core]
# Run everything in sandboxes, or alias it for per-task routing (recommended):
executor = LocalExecutor,sandbox:airflow_provider_sandbox.executors.sandbox_executor.SandboxExecutor

[logging]
# REQUIRED: the executor refuses to start without it — logs live in ephemeral
# sandboxes and must be shipped to remote storage by the in-sandbox supervisor.
remote_logging = True
remote_base_log_folder = s3://my-airflow-logs/

[sandbox]
provider = daytona        # local | daytona | e2b | modal | islo | module:Class
poll_interval = 5
creation_batch_size = 8
default_timeout = 600
```

Per-task sizing/image mirrors `KubernetesExecutor`'s `pod_override`:

```python
BashOperator(
    task_id="train",
    bash_command="python train.py",
    executor="sandbox",
    executor_config={"sandbox_override": {"image": "daytona-medium", "cpu": 4, "memory_mb": 8192}},
)
```

## Providers & capabilities

| Provider | `kind` | file upload | async exec | kill | reattach (adopt) |
|----------|--------|:-----------:|:----------:|:----:|:----------------:|
| `local`  | delegated-run | ✅ | ✅ | ✅ | ❌ |
| `daytona`| delegated-run | ✅ | ✅ | ✅ | ✅ (labelled) |
| `e2b`    | delegated-run | ✅ | ✅ | ✅ | ❌ (opaque handle) |
| `modal`  | delegated-run | ❌ (image-baked) | ✅ | ✅ | ❌ |
| `islo`   | delegated-run | ✅ | ✅ | ❌ | ✅ (named) |

Add your own backend by subclassing `SandboxProvider` and pointing
`[sandbox] provider` at `your_module:YourProvider`.

## Design notes & honest limitations

- **Cold start**: one fresh sandbox per task try means seconds of startup
  (`create` + bundle transfer + `import airflow` + supervisor boot) on every
  backend. Best for long-running, heavyweight, isolation-sensitive tasks — not a
  drop-in replacement for a warm Celery pool on high-volume short tasks.
- **Cost**: one billable sandbox per task instance; retries multiply it.
- **Logs**: `remote_logging` is mandatory. `get_task_log` is a best-effort
  fallback only (it usually runs in the api-server process, where the executor's
  in-memory handle map is empty).
- **Adoption**: clean for named/labelled providers (Daytona, islo); best-effort
  for opaque-handle providers (E2B, Modal) — a scheduler crash can strand a
  sandbox.

## Status & upstreaming

Alpha. This is a standalone third-party provider, the sanctioned first step for
a new Airflow executor (see [`docs/UPSTREAMING.md`](docs/UPSTREAMING.md)). It is
**not** an `apache/airflow` monorepo package — the `apache-airflow-providers-*`
name is ASF-reserved.

## License

Apache-2.0.

---

This project was developed with the assistance of Claude (Anthropic); all code
was reviewed by a human maintainer who takes full responsibility for it.
