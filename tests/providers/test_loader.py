from __future__ import annotations

import pytest

from airflow_provider_sandbox.provider_loader import load_provider
from airflow_provider_sandbox.providers.base import SandboxProvider
from airflow_provider_sandbox.providers.local import LocalProvider


def test_loads_builtin_alias():
    provider = load_provider("local")
    assert isinstance(provider, LocalProvider)
    assert isinstance(provider, SandboxProvider)


def test_loads_by_fqcn():
    provider = load_provider("airflow_provider_sandbox.providers.local:LocalProvider")
    assert isinstance(provider, LocalProvider)


@pytest.mark.parametrize("bad", ["", "nope", "module.without.colon"])
def test_rejects_bad_names(bad):
    with pytest.raises((ValueError, TypeError, ImportError)):
        load_provider(bad)
