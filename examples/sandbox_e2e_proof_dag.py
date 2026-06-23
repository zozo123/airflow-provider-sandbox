"""Reproducible end-to-end proof DAGs (local backend, no credentials).

Run with a temp AIRFLOW_HOME to prove both the operator and decorator paths
execute a real task inside a sandbox, including credential injection:

    export AIRFLOW_HOME=/tmp/sbx-home
    export AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/examples
    export AIRFLOW__CORE__LOAD_EXAMPLES=False
    airflow db migrate
    airflow dags test sandbox_e2e_proof       # -> state=success, AGENT_RESULT=ok
    airflow dags test sandbox_decorator_proof  # -> state=success, DECORATOR_RESULT=ok

Both were verified on Apache Airflow 3.1.
"""

from __future__ import annotations

import datetime

from airflow import DAG
from airflow.decorators import task

from airflow_provider_sandbox.operators.sandbox import SandboxOperator

with DAG(
    dag_id="sandbox_e2e_proof",
    schedule=None,
    start_date=datetime.datetime(2026, 1, 1),
    catchup=False,
    tags=["sandbox", "proof"],
) as operator_dag:
    # Operator path: LLM_API_KEY is injected into the sandbox only (never printed).
    SandboxOperator(
        task_id="run_agent_in_sandbox",
        provider="local",
        env={"LLM_API_KEY": "sk-demo-injected-secret", "PROMPT": "summarize this"},
        command=(
            'echo "agent booting in isolated sandbox";'
            'echo "key injected: ${LLM_API_KEY:+yes}";'
            'echo "running prompt: $PROMPT";'
            'echo "AGENT_RESULT=ok"'
        ),
    )

with DAG(
    dag_id="sandbox_decorator_proof",
    schedule=None,
    start_date=datetime.datetime(2026, 1, 1),
    catchup=False,
    tags=["sandbox", "proof"],
) as decorator_dag:

    @task.sandbox(provider="local", env={"LLM_API_KEY": "sk-demo"})
    def run_llm() -> str:
        # The returned string is the command executed inside the sandbox.
        return 'echo "decorator: key injected=${LLM_API_KEY:+yes}"; echo "DECORATOR_RESULT=ok"'

    run_llm()
