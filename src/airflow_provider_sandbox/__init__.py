"""airflow-provider-sandbox: run each Airflow task in an ephemeral cloud sandbox."""

from __future__ import annotations

__version__ = "0.1.0"


def get_provider_info() -> dict:
    # Re-exported for the apache_airflow_provider entry point.
    from airflow_provider_sandbox.get_provider_info import get_provider_info as _info

    return _info()
