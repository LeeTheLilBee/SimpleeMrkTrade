from tower.tower_ir_cert_p2413 import (
    build_six_room_certification_matrix,
)


def test_pack_2413_six_room_matrix():
    matrix = build_six_room_certification_matrix()

    assert matrix["room_count"] == 6
    assert matrix["all_rooms_certified"] is True

    for room in matrix["matrix"]:
        assert room["certified"] is True
        assert all(room["checks"].values())
