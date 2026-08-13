"""
GP027 — Cross-Business Impact Graph Foundation.

Advisory graph traversal only.
"""

from __future__ import annotations

from collections import deque

try:
    from .cross_business_impact_graph import (
        CrossBusinessImpactSurface,
        ImpactGraphEdge,
        ImpactGraphNode,
        ImpactKind,
        ImpactProjection,
        ImpactPropagationState,
        ImpactSeverity,
    )

    from .operating_data_adapter_service import (
        get_operating_summaries,
    )

    from .operating_snapshot_history_service import (
        get_clouds_gp026_status_payload,
        get_projection_snapshot_deltas,
    )

except ImportError:
    from cross_business_impact_graph import (
        CrossBusinessImpactSurface,
        ImpactGraphEdge,
        ImpactGraphNode,
        ImpactKind,
        ImpactProjection,
        ImpactPropagationState,
        ImpactSeverity,
    )

    from operating_data_adapter_service import (
        get_operating_summaries,
    )

    from operating_snapshot_history_service import (
        get_clouds_gp026_status_payload,
        get_projection_snapshot_deltas,
    )


SEVERITY_RANK = {
    "low": 1,
    "moderate": 2,
    "high": 3,
    "critical": 4,
}


def get_impact_graph_nodes():
    return tuple(
        ImpactGraphNode(
            source_id=item.source_id,
            source_label=item.source_label,
            owner_visible=True,
            execution_authority=False,
        )
        for item in get_operating_summaries()
    )


def get_impact_graph_edges():
    return (
        ImpactGraphEdge(
            edge_id="impact-ob-atm-capital",
            source_id="observatory",
            target_id="atm_operations",
            kind=ImpactKind.CAPITAL.value,
            severity=ImpactSeverity.HIGH.value,
            explanation=(
                "Observatory capital performance can "
                "influence ATM expansion timing."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-ob-grounds-capital",
            source_id="observatory",
            target_id="grounds",
            kind=ImpactKind.CAPITAL.value,
            severity=ImpactSeverity.HIGH.value,
            explanation=(
                "Observatory capital performance can "
                "influence property acquisition readiness."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-tower-ob-access",
            source_id="tower",
            target_id="observatory",
            kind=(
                ImpactKind
                .ACCESS_SECURITY.value
            ),
            severity=ImpactSeverity.CRITICAL.value,
            explanation=(
                "Tower access or security problems can "
                "block protected Observatory entry."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-tower-teller-access",
            source_id="tower",
            target_id="teller",
            kind=(
                ImpactKind
                .ACCESS_SECURITY.value
            ),
            severity=ImpactSeverity.CRITICAL.value,
            explanation=(
                "Tower controls protected Teller access."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-tower-grounds-access",
            source_id="tower",
            target_id="grounds",
            kind=(
                ImpactKind
                .ACCESS_SECURITY.value
            ),
            severity=ImpactSeverity.CRITICAL.value,
            explanation=(
                "Tower controls protected Grounds access."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-tower-vault-access",
            source_id="tower",
            target_id="archive_vault",
            kind=(
                ImpactKind
                .ACCESS_SECURITY.value
            ),
            severity=ImpactSeverity.CRITICAL.value,
            explanation=(
                "Tower access state affects protected "
                "Archive Vault workflows."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-vault-tower-recovery",
            source_id="archive_vault",
            target_id="tower",
            kind=(
                ImpactKind
                .EVIDENCE_RECOVERY.value
            ),
            severity=ImpactSeverity.HIGH.value,
            explanation=(
                "Vault recovery/evidence condition can "
                "affect Tower recovery confidence."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-teller-atm-finance",
            source_id="teller",
            target_id="atm_operations",
            kind=(
                ImpactKind
                .FINANCE_VISIBILITY.value
            ),
            severity=ImpactSeverity.MODERATE.value,
            explanation=(
                "Teller financial visibility can inform "
                "ATM funding decisions."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-teller-grounds-finance",
            source_id="teller",
            target_id="grounds",
            kind=(
                ImpactKind
                .FINANCE_VISIBILITY.value
            ),
            severity=ImpactSeverity.MODERATE.value,
            explanation=(
                "Teller financial visibility can inform "
                "Grounds capital planning."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),

        ImpactGraphEdge(
            edge_id="impact-grounds-atm-priority",
            source_id="grounds",
            target_id="atm_operations",
            kind=(
                ImpactKind
                .PRIORITY_COMPETITION.value
            ),
            severity=ImpactSeverity.MODERATE.value,
            explanation=(
                "Grounds acquisition requirements can "
                "compete with ATM expansion for owner capital."
            ),
            owner_attention_relevant=True,
            execution_performed=False,
        ),
    )


def _edge_map():
    mapping = {}

    for edge in get_impact_graph_edges():
        mapping.setdefault(
            edge.source_id,
            [],
        ).append(edge)

    return mapping


def _strongest_edge(edges):
    return max(
        edges,
        key=lambda edge: (
            SEVERITY_RANK[
                edge.severity
            ],
            edge.edge_id,
        ),
    )


def project_source_impact(
    origin_source_id,
    *,
    max_hops=2,
):
    nodes = {
        node.source_id
        for node in get_impact_graph_nodes()
    }

    if origin_source_id not in nodes:
        raise KeyError(
            "Unknown impact origin source: "
            f"{origin_source_id}"
        )

    edges_by_source = _edge_map()

    queue = deque(
        [
            (
                origin_source_id,
                (origin_source_id,),
                tuple(),
            )
        ]
    )

    best_paths = {}

    while queue:
        (
            current_source,
            path,
            path_edges,
        ) = queue.popleft()

        hop_count = (
            len(path) - 1
        )

        if hop_count >= max_hops:
            continue

        for edge in edges_by_source.get(
            current_source,
            (),
        ):
            target = edge.target_id

            # Cycle-safe traversal.
            if target in path:
                continue

            next_path = (
                *path,
                target,
            )

            next_edges = (
                *path_edges,
                edge,
            )

            next_hops = (
                len(next_path) - 1
            )

            existing = best_paths.get(
                target
            )

            candidate_rank = (
                next_hops,
                -max(
                    SEVERITY_RANK[
                        item.severity
                    ]
                    for item
                    in next_edges
                ),
                next_path,
            )

            if existing is not None:
                if (
                    candidate_rank
                    >= existing["rank"]
                ):
                    continue

            best_paths[target] = {
                "path": next_path,
                "edges": next_edges,
                "rank": candidate_rank,
            }

            queue.append(
                (
                    target,
                    next_path,
                    next_edges,
                )
            )

    node_labels = {
        node.source_id: node.source_label
        for node in get_impact_graph_nodes()
    }

    projections = []

    for target_id, info in (
        best_paths.items()
    ):
        path = info["path"]
        path_edges = info["edges"]

        strongest = (
            _strongest_edge(
                path_edges
            )
        )

        hop_count = (
            len(path) - 1
        )

        owner_attention_required = (
            strongest.severity
            in {
                "high",
                "critical",
            }
            and any(
                edge
                .owner_attention_relevant
                for edge in path_edges
            )
        )

        origin_label = (
            node_labels[
                origin_source_id
            ]
        )

        target_label = (
            node_labels[target_id]
        )

        projections.append(
            ImpactProjection(
                projection_id=(
                    "impact-projection-"
                    f"{origin_source_id}-"
                    f"{target_id}"
                ),

                origin_source_id=(
                    origin_source_id
                ),

                impacted_source_id=(
                    target_id
                ),

                hop_count=hop_count,

                propagation_state=(
                    ImpactPropagationState
                    .DIRECT.value
                    if hop_count == 1
                    else ImpactPropagationState
                    .INDIRECT.value
                ),

                strongest_kind=(
                    strongest.kind
                ),

                strongest_severity=(
                    strongest.severity
                ),

                path=path,

                soulaana_what_it_affects=(
                    f"A change in {origin_label} "
                    f"can affect {target_label}"
                    + (
                        " directly."
                        if hop_count == 1
                        else
                        " through another "
                        "Simplee operating dependency."
                    )
                ),

                soulaana_why_it_matters=(
                    strongest.explanation
                ),

                soulaana_owner_attention=(
                    "Keep this relationship in the "
                    "owner attention picture."
                    if owner_attention_required
                    else
                    "This relationship can remain "
                    "background context for now."
                ),

                soulaana_what_can_wait=(
                    "No downstream action should occur "
                    "from the graph alone; use the owning "
                    "application when deeper work is needed."
                ),

                owner_attention_required=(
                    owner_attention_required
                ),

                downstream_execution_performed=False,
            )
        )

    return tuple(
        sorted(
            projections,
            key=lambda item: (
                item.hop_count,
                -SEVERITY_RANK[
                    item.strongest_severity
                ],
                item.impacted_source_id,
            ),
        )
    )


def get_changed_source_impact_projections():
    deltas = (
        get_projection_snapshot_deltas()
    )

    changed_sources = tuple(
        delta.source_id
        for delta in deltas
        if delta.change_state
        == "changed"
    )

    projections = []

    for source_id in changed_sources:
        projections.extend(
            project_source_impact(
                source_id,
                max_hops=2,
            )
        )

    # Deduplicate per origin + impacted source.
    unique = {}

    for item in projections:
        key = (
            item.origin_source_id,
            item.impacted_source_id,
        )

        unique.setdefault(
            key,
            item,
        )

    return tuple(
        sorted(
            unique.values(),
            key=lambda item: (
                item.origin_source_id,
                item.hop_count,
                -SEVERITY_RANK[
                    item.strongest_severity
                ],
                item.impacted_source_id,
            ),
        )
    )


def get_impact_projection(
    origin_source_id,
    impacted_source_id,
):
    for item in project_source_impact(
        origin_source_id
    ):
        if (
            item.impacted_source_id
            == impacted_source_id
        ):
            return item

    raise KeyError(
        "No impact projection from "
        f"{origin_source_id} to "
        f"{impacted_source_id}"
    )


def get_cross_business_impact_surface():
    nodes = get_impact_graph_nodes()
    edges = get_impact_graph_edges()

    projections = (
        get_changed_source_impact_projections()
    )

    origins = {
        item.origin_source_id
        for item in projections
    }

    return CrossBusinessImpactSurface(
        title=(
            "Cross-Business Impact Graph"
        ),

        nodes=nodes,
        edges=edges,
        projections=projections,

        node_count=len(nodes),
        edge_count=len(edges),
        projection_count=len(
            projections
        ),

        origin_source_count=len(
            origins
        ),

        owner_attention_projection_count=sum(
            item.owner_attention_required
            for item in projections
        ),

        execution_performed=False,

        boundary_notice=(
            "The impact graph is advisory. "
            "It explains relationships and potential "
            "owner consequences but cannot move capital, "
            "change permissions, reprioritize businesses, "
            "or execute downstream work."
        ),
    )


def get_cross_business_impact_surface_payload():
    return (
        get_cross_business_impact_surface()
        .to_dict()
    )


def get_clouds_gp027_status_payload():
    gp026 = (
        get_clouds_gp026_status_payload()
    )

    surface = (
        get_cross_business_impact_surface()
    )

    ob_to_atm = (
        get_impact_projection(
            "observatory",
            "atm_operations",
        )
    )

    ob_to_grounds = (
        get_impact_projection(
            "observatory",
            "grounds",
        )
    )

    safe = (
        gp026["status"] == "ready"
        and gp026["safe_to_continue"]
        is True

        and surface.node_count == 6

        and surface.edge_count == 10

        and surface.origin_source_count == 1

        and surface.projection_count >= 2

        and ob_to_atm.strongest_kind
        == "capital"

        and ob_to_atm.strongest_severity
        == "high"

        and ob_to_grounds
        .strongest_kind
        == "capital"

        and ob_to_grounds
        .strongest_severity
        == "high"

        and surface.execution_performed
        is False

        and all(
            edge.execution_performed
            is False
            for edge in surface.edges
        )

        and all(
            item.downstream_execution_performed
            is False
            for item in surface.projections
        )
    )

    return {
        "pack": "GP027",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "CROSS-BUSINESS "
            "IMPACT GRAPH FOUNDATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "node_count": (
            surface.node_count
        ),

        "edge_count": (
            surface.edge_count
        ),

        "projection_count": (
            surface.projection_count
        ),

        "origin_source_count": (
            surface.origin_source_count
        ),

        "owner_attention_projection_count": (
            surface
            .owner_attention_projection_count
        ),

        "observatory_impacts_atm": True,

        "observatory_impacts_grounds": True,

        "tower_security_dependency_modeled": True,

        "capital_dependency_modeled": True,

        "finance_visibility_dependency_modeled": True,

        "priority_competition_modeled": True,

        "execution_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP028 — EXECUTIVE OWNER AGENDA "
            "/ TIME-HORIZON PRIORITIZATION"
        ),
    }
