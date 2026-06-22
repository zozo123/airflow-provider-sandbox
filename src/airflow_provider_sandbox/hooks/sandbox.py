"""``SandboxHook`` — resolves provider credentials from an Airflow Connection.

Credentials are never passed as method args (crabbox-style env-only). This hook
lets operators/tooling reach the configured provider for ad-hoc sandbox use.
"""

from __future__ import annotations

from typing import Any

from airflow.hooks.base import BaseHook

from airflow_provider_sandbox.provider_loader import load_provider
from airflow_provider_sandbox.providers.base import SandboxProvider


class SandboxHook(BaseHook):
    conn_name_attr = "sandbox_conn_id"
    default_conn_name = "sandbox_default"
    conn_type = "sandbox"
    hook_name = "Sandbox"

    def __init__(self, sandbox_conn_id: str = default_conn_name) -> None:
        super().__init__()
        self.sandbox_conn_id = sandbox_conn_id

    def get_provider(self) -> SandboxProvider:
        conn = self.get_connection(self.sandbox_conn_id)
        extra: dict[str, Any] = conn.extra_dejson or {}
        provider_name = extra.get("provider") or conn.host or "local"
        provider = load_provider(provider_name)
        provider.authenticate()
        return provider
