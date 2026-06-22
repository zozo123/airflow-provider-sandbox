"""Example DAG routing tasks to the SandboxExecutor.

Use with a multi-executor config so only these tasks run in sandboxes:

    [core]
    executor = LocalExecutor,sandbox:airflow_provider_sandbox.executors.sandbox_executor.SandboxExecutor

    [logging]
    remote_logging = True
    remote_base_log_folder = s3://my-airflow-logs/

    [sandbox]
    provider = daytona
"""

from __future__ import annotations

import datetime

try:  # Airflow 3 Task SDK import root, with a 2.x fallback.
    from airflow.sdk import DAG
except ImportError:
    from airflow import DAG

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

with DAG(
    dag_id="sandbox_demo",
    schedule="@daily",
    start_date=datetime.datetime(2026, 1, 1),
    catchup=False,
    default_args={"executor": "sandbox"},
) as dag:

    train = BashOperator(
        task_id="train_model",
        bash_command="python /opt/train.py --epochs 5",
        executor="sandbox",
        # Per-task sandbox sizing/image — parallels K8s executor_config["pod_override"].
        executor_config={
            "sandbox_override": {
                "image": "daytona-medium",
                "cpu": 4,
                "memory_mb": 8192,
                "timeout": 1800,
                "env": {"WANDB_MODE": "offline"},
            }
        },
    )

    def _score() -> None:
        print("runs in its own ephemeral sandbox")

    score = PythonOperator(task_id="score", python_callable=_score, executor="sandbox")

    train >> score
