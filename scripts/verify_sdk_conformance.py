#!/usr/bin/env python3
"""Verify that each backend's SDK call sites exist on the real installed SDKs.

This needs no API keys — it only checks that the methods/attributes/parameters
the backends use are actually present in daytona / e2b / modal / islo. Install
the SDKs you want to check (``pip install daytona e2b modal islo``) and run:

    python scripts/verify_sdk_conformance.py

Missing SDKs are skipped (reported), not failed.
"""

from __future__ import annotations

import inspect
import sys

ok: list[str] = []
bad: list[str] = []
skipped: list[str] = []


def _has(obj, attr: str) -> bool:
    return attr in dir(obj)


def check_daytona() -> None:
    try:
        import daytona
        from daytona import (
            CreateSandboxFromSnapshotParams as CP,
            Daytona,
            Sandbox,
            SessionExecuteRequest as SER,
        )
    except ImportError:
        skipped.append("daytona")
        return
    for m in ("create", "get", "delete"):
        (ok if hasattr(Daytona, m) else bad).append(f"daytona.Daytona.{m}")
    for a in ("fs", "process", "delete"):
        (ok if _has(Sandbox, a) else bad).append(f"daytona.Sandbox.{a}")
    cpf = set(getattr(CP, "model_fields", {}))
    for f in ("snapshot", "ephemeral", "auto_stop_interval", "labels", "env_vars"):
        (ok if f in cpf else bad).append(f"daytona.CreateParams.{f}")
    serf = set(getattr(SER, "model_fields", {}))
    for f in ("command", "run_async"):
        (ok if f in serf else bad).append(f"daytona.SessionExecuteRequest.{f}")
    _ = daytona


def check_e2b() -> None:
    try:
        from e2b import Sandbox
        from e2b.sandbox_sync.commands.command import Commands
    except ImportError:
        skipped.append("e2b")
        return
    (ok if hasattr(Sandbox, "create") else bad).append("e2b.Sandbox.create")
    for a in ("sandbox_id", "commands", "files"):
        (ok if _has(Sandbox, a) else bad).append(f"e2b.Sandbox.{a}")
    (ok if hasattr(Sandbox, "kill") else bad).append("e2b.Sandbox.kill")
    params = inspect.signature(Commands.run).parameters
    for p in ("background", "envs", "cwd"):
        (ok if p in params else bad).append(f"e2b.Commands.run({p})")


def check_modal() -> None:
    try:
        import modal
        from modal.container_process import ContainerProcess
    except ImportError:
        skipped.append("modal")
        return
    (ok if hasattr(modal.App, "lookup") else bad).append("modal.App.lookup")
    for m in ("from_registry", "debian_slim"):
        (ok if hasattr(modal.Image, m) else bad).append(f"modal.Image.{m}")
    for m in ("create", "exec", "terminate"):
        (ok if hasattr(modal.Sandbox, m) else bad).append(f"modal.Sandbox.{m}")
    (ok if _has(modal.Sandbox, "object_id") else bad).append("modal.Sandbox.object_id")
    for m in ("poll", "returncode", "stdout"):
        (ok if hasattr(ContainerProcess, m) else bad).append(f"modal.ContainerProcess.{m}")


def check_islo() -> None:
    try:
        from islo.sandboxes.client import SandboxesClient
        from islo.types.exec_result_response import ExecResultResponse
    except ImportError:
        skipped.append("islo")
        return
    for m in ("create_sandbox", "exec_in_sandbox", "get_exec_result", "delete_sandbox"):
        (ok if hasattr(SandboxesClient, m) else bad).append(f"islo.SandboxesClient.{m}")
    cs = inspect.signature(SandboxesClient.create_sandbox).parameters
    for p in ("name", "image", "env", "vcpus", "memory_mb", "disk_gb"):
        (ok if p in cs else bad).append(f"islo.create_sandbox({p})")
    ex = inspect.signature(SandboxesClient.exec_in_sandbox).parameters
    for p in ("command", "env", "timeout_secs", "workdir"):
        (ok if p in ex else bad).append(f"islo.exec_in_sandbox({p})")
    erf = set(getattr(ExecResultResponse, "model_fields", {}))
    for f in ("exec_id", "exit_code", "stdout", "stderr"):
        (ok if f in erf else bad).append(f"islo.ExecResultResponse.{f}")


def main() -> int:
    for fn in (check_daytona, check_e2b, check_modal, check_islo):
        fn()
    total = len(ok) + len(bad)
    print(f"PASS {len(ok)} / {total} SDK conformance checks")
    if skipped:
        print("skipped (SDK not installed):", ", ".join(skipped))
    if bad:
        print("MISMATCHES:")
        for b in bad:
            print("  x", b)
        return 1
    if total == 0:
        # No SDKs installed → nothing was actually verified. Do NOT report a
        # vacuous "OK" (this previously read as a pass when it verified nothing).
        print(
            "NOTHING VERIFIED: install the SaaS SDKs to run real conformance — "
            "pip install daytona e2b modal islo"
        )
        return 2
    print("OK: all checked call sites match the installed SDKs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
