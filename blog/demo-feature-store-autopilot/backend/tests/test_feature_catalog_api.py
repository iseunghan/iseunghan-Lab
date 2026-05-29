"""Tests for /api/features/catalog endpoint."""

import pytest

from app.services.feature_registry import get_catalog_items, get_feature_view_names


class TestFeatureCatalogAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as c:
            yield c

    def test_catalog_contains_expected_feature_views(self, client):
        response = client.get("/api/features/catalog")

        assert response.status_code == 200
        payload = response.json()
        assert payload["entity_name"] == "vehicle"
        assert payload["entity_join_keys"] == ["vehicle_id"]

        feature_views = payload["feature_views"]
        names = [fv["name"] for fv in feature_views]
        assert names == get_feature_view_names()

        sensor = feature_views[0]
        assert sensor["ttl_hours"] == get_catalog_items()[0]["ttl_hours"]
        assert sensor["online"] is True
        assert "avg_speed_10s" in sensor["features"]
