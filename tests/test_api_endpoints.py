"""
Tests for core API endpoints (diary, recipes, foods, analytics, etc.)
Verifies that endpoints respond correctly and auth decorators are applied.
"""

import pytest


class TestFodmapEndpoints:
    """Tests for FODMAP reference data endpoints."""

    def test_get_categories(self, client):
        """GET /fodmap/categories should return category list."""
        resp = client.get('/api/v1/fodmap/categories')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, (list, dict))

    def test_get_foods_requires_category(self, client):
        """GET /fodmap/foods without category should return 400."""
        resp = client.get('/api/v1/fodmap/foods')
        assert resp.status_code == 400

    def test_get_foods_with_category(self, client):
        """GET /fodmap/foods with category should return food list."""
        resp = client.get('/api/v1/fodmap/foods?category=Fructose')
        assert resp.status_code == 200

    def test_auth_enforced_with_bad_key(self, client):
        """FODMAP endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401

    def test_scope_enforced(self, app, db_session, client):
        """FODMAP endpoints should require read:fodmap scope."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        raw_key, key_obj = _create_api_key(db_session, scopes='read:diary')
        resp = client.get('/api/v1/fodmap/categories',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 403

        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()


class TestDiaryEndpoints:
    """Tests for diary API endpoints."""

    def test_get_entries_web(self, client):
        """GET /diary/entries should work for web users."""
        resp = client.get('/api/v1/diary/entries')
        assert resp.status_code == 200

    def test_get_day_web(self, client):
        """GET /diary/day/<date> should work for web users."""
        resp = client.get('/api/v1/diary/day/2026-03-01')
        assert resp.status_code == 200

    def test_get_trends_web(self, client):
        """GET /diary/trends should work for web users."""
        resp = client.get('/api/v1/diary/trends')
        assert resp.status_code == 200

    def test_get_weekly_web(self, client):
        """GET /diary/weekly should work for web users."""
        resp = client.get('/api/v1/diary/weekly')
        assert resp.status_code == 200

    def test_diary_auth_enforced(self, client):
        """Diary endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/diary/entries',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401

    def test_diary_scope_enforced(self, app, db_session, client):
        """Diary endpoints should require read:diary scope."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        raw_key, key_obj = _create_api_key(db_session, scopes='read:analytics')
        resp = client.get('/api/v1/diary/entries',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 403

        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()

    def test_create_meal_requires_write_scope(self, app, db_session, client):
        """POST /diary/meals should require write:diary scope."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        raw_key, key_obj = _create_api_key(db_session, scopes='read:diary')
        resp = client.post('/api/v1/diary/meals',
                           headers={'X-API-Key': raw_key},
                           json={'date': '2026-03-01', 'meal_type': 'Lunch'})
        assert resp.status_code == 403

        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()


class TestRecipeEndpoints:
    """Tests for recipe API endpoints."""

    def test_get_recipes_web(self, client):
        """GET /recipes should work for web users."""
        resp = client.get('/api/v1/recipes')
        assert resp.status_code == 200

    def test_recipes_auth_enforced(self, client):
        """Recipe endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/recipes',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401

    def test_recipes_scope_enforced(self, app, db_session, client):
        """Recipe endpoints should require read:recipes scope."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        raw_key, key_obj = _create_api_key(db_session, scopes='read:diary')
        resp = client.get('/api/v1/recipes',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 403

        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()


class TestAnalyticsEndpoints:
    """Tests for analytics API endpoints."""

    def test_dashboard_web(self, client):
        """GET /dashboard should work for web users."""
        resp = client.get('/api/v1/dashboard')
        assert resp.status_code == 200

    def test_analytics_auth_enforced(self, client):
        """Analytics endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/dashboard',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401

    def test_symptom_patterns_web(self, client):
        """GET /analytics/symptom-patterns should work for web users."""
        resp = client.get('/api/v1/analytics/symptom-patterns')
        assert resp.status_code == 200

    def test_analytics_scope_enforced(self, app, db_session, client):
        """Analytics endpoints should require read:analytics scope."""
        from tests.conftest import _create_api_key
        from models.security import ApiAccessLog

        raw_key, key_obj = _create_api_key(db_session, scopes='read:diary')
        resp = client.get('/api/v1/dashboard',
                          headers={'X-API-Key': raw_key})
        assert resp.status_code == 403

        ApiAccessLog.query.filter_by(key_id=key_obj.id).delete()
        db_session.delete(key_obj)
        db_session.commit()


class TestSearchEndpoints:
    """Tests for search API endpoints."""

    def test_global_search_web(self, client):
        """GET /search/global should work for web users."""
        resp = client.get('/api/v1/search/global?q=apple')
        assert resp.status_code == 200

    def test_search_auth_enforced(self, client):
        """Search endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/search/global?q=apple',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401


class TestExportEndpoints:
    """Tests for export API endpoints."""

    def test_export_diary_requires_dates(self, client):
        """GET /export/diary without dates should return 400."""
        resp = client.get('/api/v1/export/diary')
        assert resp.status_code == 400

    def test_export_diary_with_dates(self, client):
        """GET /export/diary with dates should work for web users."""
        resp = client.get('/api/v1/export/diary?start_date=2026-01-01&end_date=2026-03-01')
        assert resp.status_code == 200

    def test_export_auth_enforced(self, client):
        """Export endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/export/diary',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401


class TestEducationEndpoints:
    """Tests for education API endpoints."""

    def test_get_education_web(self, client):
        """GET /education should work for web users."""
        resp = client.get('/api/v1/education')
        assert resp.status_code == 200

    def test_education_auth_enforced(self, client):
        """Education endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/education',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401


class TestSettingsEndpoints:
    """Tests for settings/help API endpoints."""

    def test_get_help_web(self, client):
        """GET /help should work for web users."""
        resp = client.get('/api/v1/help')
        assert resp.status_code == 200

    def test_help_auth_enforced(self, client):
        """Help endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/help',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401


class TestUSDAEndpoints:
    """Tests for USDA reference data endpoints."""

    def test_usda_categories_web(self, client):
        """GET /usda/categories should work for web users."""
        resp = client.get('/api/v1/usda/categories')
        assert resp.status_code == 200

    def test_usda_search_web(self, client):
        """GET /usda/search should work for web users."""
        resp = client.get('/api/v1/usda/search?q=apple')
        assert resp.status_code == 200

    def test_usda_auth_enforced(self, client):
        """USDA endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/usda/categories',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401


class TestAusnutEndpoints:
    """Tests for AUSNUT reference data endpoints."""

    def test_ausnut_search_web(self, client):
        """GET /ausnut/search should work for web users."""
        resp = client.get('/api/v1/ausnut/search?q=milk')
        assert resp.status_code == 200

    def test_ausnut_auth_enforced(self, client):
        """AUSNUT endpoints should reject invalid API keys."""
        resp = client.get('/api/v1/ausnut/search?q=milk',
                          headers={'X-API-Key': 'bad-key'})
        assert resp.status_code == 401
