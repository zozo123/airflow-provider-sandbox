"""The marquee use case: run an LLM agent inside an ephemeral, isolated sandbox.

Why this is the killer app for a sandbox executor/operator:
  * LLM agents run *model-generated* code/tool-calls — you do not want that
    executing on a shared Airflow worker with broad credentials and network.
  * A fresh, disposable sandbox per run gives strong isolation, a clean
    filesystem, and a blast radius of exactly one task.
  * The LLM API key is injected *into the sandbox only* (via ``env`` resolved
    from an Airflow Variable/Connection) and never touches the worker's
    environment or logs.

This pattern composes naturally with an agent toolset: the command launched in
the sandbox can be an agent runner that loads tools/"skills" and calls the model
(e.g. a future ``@task.agent`` / ``AgentOperator`` that hands the sandbox an
``AgentSkillsToolset`` and the injected model credentials).
"""

from __future__ import annotations

import datetime

from airflow import DAG
from airflow.decorators import task

# In production, resolve the key from a Variable or Connection so it is never in code:
#   from airflow.models import Variable
#   ANTHROPIC_API_KEY = Variable.get("anthropic_api_key")
ANTHROPIC_API_KEY = "{{ var.value.get('anthropic_api_key', 'sk-ant-REPLACE') }}"

# A tiny agent runner shipped into the sandbox. In a real setup this would be an
# agent framework entrypoint; here it shows the model key arriving in-sandbox and
# a model call being made (stubbed) without the key ever leaving the sandbox.
AGENT_RUNNER = r'''
import os, json, sys
key = os.environ.get("ANTHROPIC_API_KEY", "")
assert key, "model credentials were not injected into the sandbox"
prompt = os.environ.get("AGENT_PROMPT", "")
# A real agent would call the model + run its generated tool-calls here, e.g.:
#   from anthropic import Anthropic
#   client = Anthropic(api_key=key)
#   msg = client.messages.create(model="claude-opus-4-8", max_tokens=512,
#                                messages=[{"role": "user", "content": prompt}])
# We keep the demo offline but prove the wiring:
print(json.dumps({
    "sandbox": True,
    "model_key_present": bool(key),
    "model_key_len": len(key),     # length only — never echo the secret
    "prompt": prompt,
    "result": "agent completed in isolated sandbox",
}))
'''

with DAG(
    dag_id="agent_in_sandbox",
    schedule=None,
    start_date=datetime.datetime(2026, 1, 1),
    catchup=False,
    tags=["sandbox", "llm", "agent"],
) as dag:

    @task.sandbox(
        provider="daytona",  # or "local" to try offline; "e2b"/"modal"/"islo"
        image="python:3.12-slim",
        env={
            "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,  # injected ONLY into the sandbox
            "AGENT_PROMPT": "Summarize today's pipeline run and flag anomalies.",
        },
        sandbox_timeout=900,
    )
    def run_agent() -> str:
        # The returned string is the command executed inside the sandbox.
        # base64 keeps the runner intact regardless of shell quoting.
        import base64

        b64 = base64.b64encode(AGENT_RUNNER.encode()).decode()
        return f'python -c "import base64;exec(base64.b64decode(\'{b64}\').decode())"'

    run_agent()
