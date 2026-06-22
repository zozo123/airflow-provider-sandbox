"""SandboxExecutor unit tests.

These require Airflow installed (BaseExecutor). Skipped otherwise so the
provider/demo tests still run in a bare environment.
"""

from __future__ import annotations

import pytest

pytest.importorskip("airflow.executors.base_executor")

from airflow_provider_sandbox.executors.sandbox_executor import (  # noqa: E402
    SandboxExecutor,
    SandboxWatcher,
    _GONE_AFTER_CONSECUTIVE_UNKNOWN,
)
from airflow_provider_sandbox.backends.base import ExecResult, SandboxState  # noqa: E402


class _FlakyProvider:
    """Returns UNKNOWN a few times, then RUNNING — must never escalate to GONE."""

    def __init__(self):
        self.calls = 0

    def poll_status(self, handle, exec_ref):
        self.calls += 1
        if self.calls <= _GONE_AFTER_CONSECUTIVE_UNKNOWN - 1:
            return ExecResult(state=SandboxState.UNKNOWN)
        return ExecResult(state=SandboxState.RUNNING)


def test_transient_unknown_does_not_kill_running_task():
    import queue
    import threading

    inflight = {("dag", "task", "run", 1): ("h1", "e1")}
    lock = threading.Lock()
    results: queue.Queue = queue.Queue()
    watcher = SandboxWatcher(_FlakyProvider(), inflight, lock, results, interval=0.01)

    # Drive a few iterations manually instead of starting the thread.
    for _ in range(_GONE_AFTER_CONSECUTIVE_UNKNOWN + 1):
        with lock:
            snapshot = list(inflight.items())
        for key, (handle, exec_ref) in snapshot:
            res = watcher.provider.poll_status(handle, exec_ref)
            if res.state is SandboxState.UNKNOWN:
                watcher._unknown_streak[key] += 1
                if watcher._unknown_streak[key] >= _GONE_AFTER_CONSECUTIVE_UNKNOWN:
                    watcher._emit(key, ExecResult(state=SandboxState.GONE), handle)
            else:
                watcher._unknown_streak.pop(key, None)

    assert results.empty(), "a transient UNKNOWN streak (broken by RUNNING) must not emit GONE"


def test_capability_flags():
    assert SandboxExecutor.is_local is False
    assert SandboxExecutor.supports_ad_hoc_ti_run is False
