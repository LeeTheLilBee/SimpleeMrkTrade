from web.hosted_tower import app


def test_hosted_health():
    client = app.test_client()

    response = client.get(
        "/tower/healthz"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "ok": True
    }

    assert (
        response.headers.get(
            "X-Simplee-Entrypoint"
        )
        == "web.hosted_tower:app"
    )
