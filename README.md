# Airflow sandbox execution prototypes

> Experimental implementation workspace for exploring isolated execution in Apache Airflow.

This repository is **not the canonical Airflow architecture or roadmap**. Decisions about Airflow APIs, provider placement, and upstream acceptance belong in [`apache/airflow`](https://github.com/apache/airflow).

Canonical origin references:

- [`apache/airflow#68407`](https://github.com/apache/airflow/pull/68407) — Monty Code Mode / restricted generated orchestration.
- [`apache/airflow#68845`](https://github.com/apache/airflow/issues/68845) — future whole-task sandbox-backed Executor.
- [`apache/airflow#69862`](https://github.com/apache/airflow/issues/69862) — task-scoped sandbox job Operator.
- [`apache/airflow#68847`](https://github.com/apache/airflow/pull/68847) — historical oversized prototype and review discussion that must be split into focused changes.

## Canonical execution surfaces

The work is divided into four separate Airflow surfaces. They are not maturity or security levels and should not be implemented as one universal API.

| Surface | What executes in isolation | Lifecycle owner |
|---|---|---|
| **Monty Code Mode** | Restricted generated orchestration over registered tools | `AgentOperator` |
| **`SandboxToolset`** | General model-generated code while the credentialed agent remains outside | `AgentOperator` session |
| **Sandbox job Operator** | One author-declared external image, command, or job | Operator + Trigger |
| **Sandbox-backed Executor** | Complete Task SDK `ExecuteTask` workload | Scheduler + Executor |

The repository may contain experiments for more than one surface, but each upstream PR must address only one lifecycle contract.

## Repository purpose

Use this repository for:

- implementation experiments;
- third-party provider prototypes;
- deterministic lifecycle and fault-injection tests;
- local Docker Sandboxes (`sbx`) proof work;
- hosted runtime conformance experiments;
- design evidence before focused upstream Airflow PRs.

Do not treat this repository as:

- an accepted Airflow public API;
- an official Apache Airflow provider;
- proof that all sandbox runtimes have equivalent semantics;
- a production-readiness certification;
- the source of truth for Airflow architecture decisions.

## Active workstreams

### Toolset

[`#4`](https://github.com/zozo123/airflow-provider-sandbox/issues/4) tracks extracting a clean Common AI `SandboxToolset` PR for agent-scoped generated-code execution.

The intended boundary is:

```text
Airflow task / AgentOperator
├── LLM client and credentials
├── agent state
├── registered privileged tools
└── SandboxToolset
    └── isolated generated-code runtime
```

The agent remains outside; only explicitly delegated computation enters the sandbox.

### Operator

[`#2`](https://github.com/zozo123/airflow-provider-sandbox/issues/2) tracks the task-scoped Docker sandbox job Operator and its real local `sbx` conformance matrix.

Prototype PR: [`zozo123/airflow#3`](https://github.com/zozo123/airflow/pull/3).

The current PR is intentionally stacked on the historical prototype branch. It is **not upstream-ready** until its dependencies are isolated, it is rebased onto current Airflow `main`, and the full Breeze and real `sbx` test matrix passes.

### Executor

[`#3`](https://github.com/zozo123/airflow-provider-sandbox/issues/3) tracks splitting the whole-task Executor prototype into focused PRs:

1. generic Core revocation safety;
2. lifecycle models and deterministic fault-injection fake;
3. common Executor state machine;
4. Docker Sandboxes non-production reference Executor;
5. production-oriented hosted Executor after live conformance.

### Conformance

[`#5`](https://github.com/zozo123/airflow-provider-sandbox/issues/5) tracks shared observable guarantees:

- deterministic request and generation identity;
- idempotent launch;
- recovery by Airflow-owned identity;
- exact-identity cancellation;
- fencing before retry;
- reconnectable logs;
- provider-enforced TTL;
- leak detection;
- fault injection;
- security and production-readiness evidence.

A stable common runtime SPI must not be extracted from one implementation alone.

## Safety invariants

Across Operator and Executor experiments:

- an ambiguous launch must not create overlapping duplicate work;
- a successor generation starts only after predecessor absence or successful fencing;
- cancellation targets the exact sandbox and execution identity;
- worker, Triggerer, and scheduler restarts must reconnect or fail closed;
- unknown state is not considered safe termination;
- external resources expire independently of Airflow;
- local scratch or status files writable by sandboxed code are not trusted security boundaries;
- Docker Sandboxes is treated as a local development and conformance backend unless stronger guarantees are separately proven.

## Provider strategy

Hosted runtime integrations should initially be developed and tested as third-party providers.

An official Apache Airflow provider requires the current Airflow governance process, including:

- a working implementation;
- at least two stewards;
- an Airflow committer sponsor;
- tests and documentation;
- a continuous live system-test plan;
- public dev-list discussion and incubation commitments.

The Islo integration should first prove its API and lifecycle through public live conformance before an official provider proposal.

## Current status

Experimental.

Some happy paths have been demonstrated, but no component in this repository should be described as production-ready without satisfying the gates in issue #5.

The active prototype branches and PRs remain implementation evidence to be split, tested, and proposed through focused Airflow changes.

## License

Apache-2.0.
