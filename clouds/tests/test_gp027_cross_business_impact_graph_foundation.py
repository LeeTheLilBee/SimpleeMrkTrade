import pytest

from clouds.cross_business_impact_graph_service import (
    get_changed_source_impact_projections,
    get_clouds_gp027_status_payload,
    get_cross_business_impact_surface,
    get_cross_business_impact_surface_payload,
    get_impact_graph_edges,
    get_impact_graph_nodes,
    get_impact_projection,
    project_source_impact,
)


EXPECTED_NODES = {
    "observatory",
    "tower",
    "teller",
    "grounds",
    "archive_vault",
    "atm_operations",
}


def test_gp027_six_nodes():
    nodes = get_impact_graph_nodes()

    assert len(nodes) == 6

    assert {
        node.source_id
        for node in nodes
    } == EXPECTED_NODES


def test_gp027_ten_edges():
    assert len(
        get_impact_graph_edges()
    ) == 10


def test_gp027_nodes_have_no_execution_authority():
    assert all(
        node.execution_authority
        is False
        for node in get_impact_graph_nodes()
    )


def test_gp027_edges_execute_nothing():
    assert all(
        edge.execution_performed
        is False
        for edge in get_impact_graph_edges()
    )


def test_gp027_observatory_directly_impacts_atm():
    projection = (
        get_impact_projection(
            "observatory",
            "atm_operations",
        )
    )

    assert projection.hop_count == 1

    assert (
        projection.propagation_state
        == "direct"
    )

    assert (
        projection.strongest_kind
        == "capital"
    )

    assert (
        projection.strongest_severity
        == "high"
    )


def test_gp027_observatory_directly_impacts_grounds():
    projection = (
        get_impact_projection(
            "observatory",
            "grounds",
        )
    )

    assert projection.hop_count == 1

    assert (
        projection.strongest_kind
        == "capital"
    )


def test_gp027_tower_impacts_observatory():
    projection = (
        get_impact_projection(
            "tower",
            "observatory",
        )
    )

    assert (
        projection.strongest_kind
        == "access_security"
    )

    assert (
        projection.strongest_severity
        == "critical"
    )


def test_gp027_archive_vault_can_propagate_through_tower():
    projections = (
        project_source_impact(
            "archive_vault",
            max_hops=2,
        )
    )

    ids = {
        item.impacted_source_id
        for item in projections
    }

    assert "tower" in ids
    assert "observatory" in ids


def test_gp027_cycle_safe():
    projections = (
        project_source_impact(
            "archive_vault",
            max_hops=5,
        )
    )

    for item in projections:
        assert len(
            item.path
        ) == len(
            set(item.path)
        )


def test_gp027_unknown_origin_fails_closed():
    with pytest.raises(KeyError):
        project_source_impact(
            "missing"
        )


def test_gp027_missing_projection_fails_closed():
    with pytest.raises(KeyError):
        get_impact_projection(
            "atm_operations",
            "tower",
        )


def test_gp027_soulaana_explains_every_projection():
    for item in (
        get_changed_source_impact_projections()
    ):
        assert (
            item.soulaana_what_it_affects
        )

        assert (
            item.soulaana_why_it_matters
        )

        assert (
            item.soulaana_owner_attention
        )

        assert (
            item.soulaana_what_can_wait
        )


def test_gp027_changed_sources_are_origins():
    projections = (
        get_changed_source_impact_projections()
    )

    origins = {
        item.origin_source_id
        for item in projections
    }

    assert origins == {
            "observatory",
        }


def test_gp027_no_downstream_execution():
    assert all(
        item.downstream_execution_performed
        is False
        for item
        in get_changed_source_impact_projections()
    )


def test_gp027_surface():
    surface = (
        get_cross_business_impact_surface()
    )

    assert surface.node_count == 6
    assert surface.edge_count == 10
    assert (
        surface.origin_source_count
        == 1
    )
    assert (
        surface.execution_performed
        is False
    )


def test_gp027_surface_payload():
    payload = (
        get_cross_business_impact_surface_payload()
    )

    assert payload["node_count"] == 6
    assert payload["edge_count"] == 10

    assert len(
        payload["nodes"]
    ) == 6

    assert len(
        payload["edges"]
    ) == 10


def test_gp027_status():
    status = (
        get_clouds_gp027_status_payload()
    )

    assert status["pack"] == "GP027"

    assert (
        status["phase"]
        == "CLOUDS_PHASE_II"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status["node_count"]
        == 6
    )

    assert (
        status["edge_count"]
        == 10
    )

    assert (
        status["origin_source_count"]
        == 1
    )

    assert (
        status["observatory_impacts_atm"]
        is True
    )

    assert (
        status["observatory_impacts_grounds"]
        is True
    )

    assert (
        status[
            "tower_security_dependency_modeled"
        ]
        is True
    )

    assert (
        status["execution_performed"]
        is False
    )

    assert status["next_pack"] == (
        "GP028 — EXECUTIVE OWNER AGENDA "
        "/ TIME-HORIZON PRIORITIZATION"
    )
