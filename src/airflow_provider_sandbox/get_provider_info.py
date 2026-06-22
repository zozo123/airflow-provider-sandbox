"""Provider metadata for Airflow's ``apache_airflow_provider`` entry point.

The ``executors`` list is what makes ``SandboxExecutor`` discoverable to
``airflow providers executors`` and selectable via ``[core] executor``.
"""

from __future__ import annotations

from airflow_provider_sandbox import __version__


def get_provider_info() -> dict:
    return {
        "package-name": "airflow-provider-sandbox",
        "name": "Sandbox",
        "description": (
            "Run each Airflow task instance in an ephemeral cloud sandbox "
            "(local/Daytona/E2B/Modal/islo) behind a pluggable provider layer."
        ),
        "versions": [__version__],
        "executors": [
            "airflow_provider_sandbox.executors.sandbox_executor.SandboxExecutor",
        ],
        "task-decorators": [
            {
                "name": "sandbox",
                "class-name": "airflow_provider_sandbox.decorators.sandbox.sandbox_task",
            },
        ],
        "config": {
            "sandbox": {
                "description": "SandboxExecutor configuration.",
                "options": {
                    "provider": {
                        "description": "Backend: local|daytona|e2b|modal|islo or module:Class.",
                        "type": "string",
                        "default": "local",
                        "version_added": "0.1.0",
                        "example": "daytona",
                    },
                    "poll_interval": {
                        "description": "Watcher poll cadence in seconds.",
                        "type": "integer",
                        "default": "5",
                        "version_added": "0.1.0",
                        "example": None,
                    },
                    "creation_batch_size": {
                        "description": "Max sandboxes created per scheduler heartbeat.",
                        "type": "integer",
                        "default": "8",
                        "version_added": "0.1.0",
                        "example": None,
                    },
                },
            }
        },
    }
