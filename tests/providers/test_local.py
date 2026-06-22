"""LocalProvider exercises the full provider contract with no SaaS creds."""

from __future__ import annotations

import time

from airflow_provider_sandbox.providers.base import SandboxSpec, SandboxState
from airflow_provider_sandbox.providers.local import LocalProvider


def _run_to_terminal(provider, handle, exec_ref, timeout=30):
    deadline = time.monotonic() + timeout
    res = provider.poll_status(handle, exec_ref)
    while res.state in (SandboxState.PENDING, SandboxState.RUNNING, SandboxState.UNKNOWN):
        assert time.monotonic() < deadline, "timed out"
        time.sleep(0.05)
        res = provider.poll_status(handle, exec_ref)
    return res


def test_successful_command_lifecycle():
    provider = LocalProvider()
    provider.authenticate()
    handle = provider.create_sandbox(SandboxSpec(name="t-ok", env={"X": "hi"}))
    exec_ref = provider.run(handle, ["sh", "-c", 'echo "$X"; exit 0'], env={"X": "hi"})
    res = _run_to_terminal(provider, handle, exec_ref)
    assert res.state is SandboxState.SUCCEEDED
    assert res.exit_code == 0
    _, logs = provider.fetch_logs(handle, exec_ref)
    assert any("hi" in line for line in logs)
    provider.destroy(handle)
    # After destroy the process is forgotten → GONE.
    assert provider.poll_status(handle, exec_ref).state is SandboxState.GONE


def test_failing_command_maps_to_failed():
    provider = LocalProvider()
    provider.authenticate()
    handle = provider.create_sandbox(SandboxSpec(name="t-fail"))
    exec_ref = provider.run(handle, ["sh", "-c", "exit 7"], env={})
    res = _run_to_terminal(provider, handle, exec_ref)
    assert res.state is SandboxState.FAILED
    assert res.exit_code == 7
    provider.destroy(handle)


def test_uses_spec_name_as_handle():
    provider = LocalProvider()
    handle = provider.create_sandbox(SandboxSpec(name="deterministic-name"))
    assert handle == "deterministic-name"
    provider.destroy(handle)
