"""
GP027 — Cross-Business Impact Graph Foundation.

Defines advisory relationships between Simplee operating sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ImpactKind(str, Enum):
    CAPITAL = "capital"
    ACCESS_SECURITY = "access_security"
    FINANCE_VISIBILITY = "finance_visibility"
    OPERATIONS = "operations"
    READINESS = "readiness"
    EVIDENCE_RECOVERY = "evidence_recovery"
    PRIORITY_COMPETITION = "priority_competition"


class ImpactSeverity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactPropagationState(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"


@dataclass(frozen=True)
class ImpactGraphNode:
    source_id: str
    source_label: str

    owner_visible: bool
    execution_authority: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_label": self.source_label,
            "owner_visible": self.owner_visible,
            "execution_authority": (
                self.execution_authority
            ),
        }


@dataclass(frozen=True)
class ImpactGraphEdge:
    edge_id: str

    source_id: str
    target_id: str

    kind: str
    severity: str

    explanation: str

    owner_attention_relevant: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "kind": self.kind,
            "severity": self.severity,
            "explanation": self.explanation,
            "owner_attention_relevant": (
                self.owner_attention_relevant
            ),
            "execution_performed": (
                self.execution_performed
            ),
        }


@dataclass(frozen=True)
class ImpactProjection:
    projection_id: str

    origin_source_id: str
    impacted_source_id: str

    hop_count: int
    propagation_state: str

    strongest_kind: str
    strongest_severity: str

    path: tuple[str, ...]

    soulaana_what_it_affects: str
    soulaana_why_it_matters: str
    soulaana_owner_attention: str
    soulaana_what_can_wait: str

    owner_attention_required: bool

    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "projection_id": self.projection_id,
            "origin_source_id": (
                self.origin_source_id
            ),
            "impacted_source_id": (
                self.impacted_source_id
            ),
            "hop_count": self.hop_count,
            "propagation_state": (
                self.propagation_state
            ),
            "strongest_kind": (
                self.strongest_kind
            ),
            "strongest_severity": (
                self.strongest_severity
            ),
            "path": list(self.path),
            "soulaana_what_it_affects": (
                self.soulaana_what_it_affects
            ),
            "soulaana_why_it_matters": (
                self.soulaana_why_it_matters
            ),
            "soulaana_owner_attention": (
                self.soulaana_owner_attention
            ),
            "soulaana_what_can_wait": (
                self.soulaana_what_can_wait
            ),
            "owner_attention_required": (
                self.owner_attention_required
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class CrossBusinessImpactSurface:
    title: str

    nodes: tuple[
        ImpactGraphNode,
        ...
    ]

    edges: tuple[
        ImpactGraphEdge,
        ...
    ]

    projections: tuple[
        ImpactProjection,
        ...
    ]

    node_count: int
    edge_count: int
    projection_count: int

    origin_source_count: int
    owner_attention_projection_count: int

    execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "nodes": [
                node.to_dict()
                for node in self.nodes
            ],
            "edges": [
                edge.to_dict()
                for edge in self.edges
            ],
            "projections": [
                item.to_dict()
                for item in self.projections
            ],
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "projection_count": (
                self.projection_count
            ),
            "origin_source_count": (
                self.origin_source_count
            ),
            "owner_attention_projection_count": (
                self
                .owner_attention_projection_count
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }
