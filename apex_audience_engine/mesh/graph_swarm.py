"""ApexGraphSwarm Coordinator.

Coordinates audience engineering sub-agents as a Directed Acyclic Graph (DAG),
enforcing deterministic task dependencies, tracing latencies, and checkpointing state.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Set


class SwarmNodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SwarmDAGNode:
    node_id: str
    action_fn: Callable[[dict[str, Any]], dict[str, Any]]
    dependencies: set[str] = field(default_factory=set)
    status: SwarmNodeStatus = SwarmNodeStatus.PENDING
    execution_time_ms: float = 0.0
    output: dict[str, Any] = field(default_factory=dict)


class ApexGraphSwarmCoordinator:
    """DAG multi-agent execution orchestrator."""

    def __init__(self) -> None:
        self.nodes: dict[str, SwarmDAGNode] = {}

    def add_node(
        self,
        node_id: str,
        action_fn: Callable[[dict[str, Any]], dict[str, Any]],
        dependencies: Optional[set[str]] = None,
    ) -> None:
        self.nodes[node_id] = SwarmDAGNode(
            node_id=node_id,
            action_fn=action_fn,
            dependencies=dependencies or set(),
        )

    def execute_dag(self, initial_state: dict[str, Any]) -> dict[str, Any]:
        """Executes all DAG nodes in topological order."""
        context: dict[str, Any] = dict(initial_state)
        executed: set[str] = set()

        while len(executed) < len(self.nodes):
            # Find eligible nodes whose dependencies have been completed
            eligible = [
                n_id
                for n_id, node in self.nodes.items()
                if n_id not in executed and node.dependencies.issubset(executed)
            ]

            if not eligible:
                raise RuntimeError("Cycle detected or unsatisfiable dependencies in ApexGraphSwarm DAG.")

            for n_id in eligible:
                node = self.nodes[n_id]
                node.status = SwarmNodeStatus.RUNNING
                t0 = time.perf_counter()

                try:
                    res = node.action_fn(context)
                    t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
                    node.execution_time_ms = round(t_elapsed_ms, 3)
                    node.output = res
                    node.status = SwarmNodeStatus.COMPLETED
                    context.update(res)
                    executed.add(n_id)
                except Exception as e:
                    node.status = SwarmNodeStatus.FAILED
                    raise RuntimeError(f"ApexGraphSwarm node '{n_id}' failed: {e}") from e

        return context
