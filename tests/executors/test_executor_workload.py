"""SandboxExecutor renders the real Task SDK supervise command + workload env."""

from __future__ import annotations

import base64

import pytest

pytest.importorskip("airflow.executors.base_executor")


def _executor(monkeypatch):
    monkeypatch.setenv("AIRFLOW__SANDBOX__PROVIDER", "local")
    from airflow_provider_sandbox.executors.sandbox_executor import SandboxExecutor

    return SandboxExecutor()


class _FakeWorkload:
    def model_dump_json(self) -> str:
        return '{"token":"jwt-123","ti":{}}'


def test_workload_renders_supervise_runner(monkeypatch):
    ex = _executor(monkeypatch)
    assert ex._render_command(_FakeWorkload()) == [
        "python",
        "-m",
        "airflow_provider_sandbox.execution_time.run_workload",
    ]


def test_workload_env_carries_serialized_workload(monkeypatch):
    monkeypatch.setenv("AIRFLOW__CORE__EXECUTION_API_SERVER_URL", "https://api/execution/")
    ex = _executor(monkeypatch)
    env = ex._workload_env(_FakeWorkload())
    assert base64.b64decode(env["AIRFLOW_SANDBOX_WORKLOAD"]).decode() == '{"token":"jwt-123","ti":{}}'
    assert env["AIRFLOW__CORE__EXECUTION_API_SERVER_URL"] == "https://api/execution/"


def test_raw_command_fallback(monkeypatch):
    ex = _executor(monkeypatch)
    assert ex._render_command(["echo", "hi"]) == ["echo", "hi"]
    assert ex._workload_env(["echo", "hi"]) == {} or "AIRFLOW_SANDBOX_WORKLOAD" not in ex._workload_env(["echo", "hi"])
