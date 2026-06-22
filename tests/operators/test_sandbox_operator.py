"""SandboxOperator runs a command in a sandbox and maps exit code to task state."""

from __future__ import annotations

import pytest

pytest.importorskip("airflow.sdk")

from airflow.exceptions import AirflowException  # noqa: E402

from airflow_provider_sandbox.operators.sandbox import SandboxOperator  # noqa: E402


def test_returns_stdout_on_success():
    op = SandboxOperator(
        task_id="ok",
        provider="local",
        command='echo "INJECTED=${SECRET:+yes}"; echo hello',
        env={"SECRET": "x"},
        poll_interval=1,
    )
    out = op.execute({})
    assert "hello" in out
    assert "INJECTED=yes" in out


def test_raises_on_nonzero_exit():
    op = SandboxOperator(task_id="bad", provider="local", command="exit 3", poll_interval=1)
    with pytest.raises(AirflowException):
        op.execute({})


def test_argv_command_form():
    op = SandboxOperator(
        task_id="argv", provider="local", command=["sh", "-c", "echo argv-form"], poll_interval=1
    )
    assert "argv-form" in op.execute({})
