#!/usr/bin/env python3
"""Concise, runnable demo of the SandboxProvider contract — no Airflow needed.

Drives the full lifecycle (create → upload → run → poll → logs → destroy) the
``SandboxExecutor`` uses, against any backend. Defaults to the ``local``
provider so it runs with zero credentials.

    python examples/demo.py                 # local subprocess backend
    SANDBOX_PROVIDER=daytona python examples/demo.py   # needs DAYTONA_API_KEY
    SANDBOX_PROVIDER=e2b     python examples/demo.py   # needs E2B_API_KEY

Run from the repo root (or `pip install -e .` first).
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from airflow_provider_sandbox.provider_loader import load_provider  # noqa: E402
from airflow_provider_sandbox.providers.base import (  # noqa: E402
    SandboxSpec,
    SandboxState,
)

POLL = 0.5
TIMEOUT = 60


def main() -> int:
    name = os.environ.get("SANDBOX_PROVIDER", "local")
    print(f"▶ provider = {name!r}")
    provider = load_provider(name)
    provider.authenticate()
    print(f"  capabilities: {provider.capabilities}")

    spec = SandboxSpec(
        name="demo-task-1",
        image=os.environ.get("SANDBOX_IMAGE"),
        env={"GREETING": "hello from the sandbox"},
        timeout=TIMEOUT,
        labels={"airflow_dag_id": "demo", "airflow_task_id": "say_hi"},
    )

    handle = provider.create_sandbox(spec)
    print(f"✔ created sandbox  handle={handle}")

    command = ["sh", "-c", 'echo "$GREETING"; echo "exit code demo"; exit 0']
    exec_ref = provider.run(handle, command, env=spec.env, timeout=spec.timeout)
    print(f"✔ started command  exec_ref={exec_ref}")

    deadline = time.monotonic() + TIMEOUT
    result = provider.poll_status(handle, exec_ref)
    while result.state in (SandboxState.PENDING, SandboxState.RUNNING, SandboxState.UNKNOWN):
        if time.monotonic() > deadline:
            print("✘ timed out waiting for terminal state")
            break
        time.sleep(POLL)
        result = provider.poll_status(handle, exec_ref)
    print(f"✔ terminal state   {result.state.value}  exit_code={result.exit_code}")

    messages, logs = provider.fetch_logs(handle, exec_ref)
    for m in messages:
        print(f"  [{m}]")
    for line in logs:
        print(f"    | {line}")

    provider.destroy(handle)
    print("✔ destroyed sandbox")

    ok = result.state is SandboxState.SUCCEEDED
    print("\n" + ("✅ DEMO PASSED" if ok else "❌ DEMO FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
