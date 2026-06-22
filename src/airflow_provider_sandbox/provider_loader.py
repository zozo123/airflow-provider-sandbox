"""Map the ``[sandbox] provider`` config value to a :class:`SandboxProvider`.

Mirrors ``crabbox --provider <name>``. Custom backends can be registered by
fully-qualified class path (``my_pkg.module:MyProvider``).
"""

from __future__ import annotations

from importlib import import_module

from airflow_provider_sandbox.providers.base import SandboxProvider

_BUILTIN: dict[str, str] = {
    "local": "airflow_provider_sandbox.providers.local:LocalProvider",
    "daytona": "airflow_provider_sandbox.providers.daytona:DaytonaProvider",
    "e2b": "airflow_provider_sandbox.providers.e2b:E2BProvider",
    "modal": "airflow_provider_sandbox.providers.modal:ModalProvider",
    "islo": "airflow_provider_sandbox.providers.islo:IsloProvider",
}


def load_provider(name: str) -> SandboxProvider:
    """Instantiate the provider named by config (built-in alias or ``mod:Class``)."""
    if not name:
        raise ValueError("[sandbox] provider is not set")
    spec = _BUILTIN.get(name.strip().lower(), name.strip())
    if ":" not in spec:
        raise ValueError(
            f"Unknown provider {name!r}. Use one of {sorted(_BUILTIN)} "
            "or a fully-qualified 'module:Class' path."
        )
    module_path, _, class_name = spec.partition(":")
    cls = getattr(import_module(module_path), class_name)
    if not (isinstance(cls, type) and issubclass(cls, SandboxProvider)):
        raise TypeError(f"{spec} is not a SandboxProvider subclass")
    return cls()
