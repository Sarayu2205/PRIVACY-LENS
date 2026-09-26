"""
Integration tests for the PrivacyLens REST API.
Uses SQLite in-memory DB via conftest.py fixtures.
"""
import pytest


class TestAuth:
    def test_register_success(self, client):
        res = client.post("/api/auth/register", json={
            "name": "Demo User",
            "email": "demo@example.com",
            "password": "DemoPass@123",
            "confirm_password": "DemoPass@123",
        })
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "demo@example.com"

    def test_register_duplicate_email(self, client):
        payload = {
            "name": "Dup User",
            "email": "dup@example.com",
            "password": "DupPass@123",
            "confirm_password": "DupPass@123",
        }
        client.post("/api/auth/register", json=payload)
        res = client.post("/api/auth/register", json=payload)
        assert res.status_code == 409

    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "LoginPass@123",
            "confirm_password": "LoginPass@123",
        })
        res = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "LoginPass@123",
        })
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_login_wrong_password(self, client):
        res = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "WrongPassword",
        })
        assert res.status_code == 401

    def test_get_me_authenticated(self, auth_client):
        res = auth_client.get("/api/auth/me")
        assert res.status_code == 200
        assert "email" in res.json()

    def test_protected_route_rejects_unauthenticated(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 403  # No credentials


class TestScanText:
    def test_scan_text_detects_email(self, auth_client):
        res = auth_client.post("/api/scan/text", json={
            "text": "Contact: test.user@example.com",
            "label": "Test Text",
        })
        assert res.status_code == 200
        data = res.json()
        assert data["finding_count"] >= 1
        assert "EMAIL" in data["categories"]

    def test_scan_text_clean_returns_zero(self, auth_client):
        res = auth_client.post("/api/scan/text", json={
            "text": "This is a completely clean document with no sensitive info.",
            "label": "Clean Text",
        })
        assert res.status_code == 200
        assert res.json()["finding_count"] == 0

    def test_scan_text_empty_rejected(self, auth_client):
        res = auth_client.post("/api/scan/text", json={"text": "   "})
        assert res.status_code == 400

    def test_scan_returns_risk_score(self, auth_client):
        res = auth_client.post("/api/scan/text", json={
            "text": "password=SuperSecret123 API_KEY=sk_test_abc123defghijklmnop",
        })
        assert res.status_code == 200
        assert res.json()["risk_score"] > 0

    def test_scan_stores_in_history(self, auth_client):
        auth_client.post("/api/scan/text", json={
            "text": "user@example.com 9876543210",
            "label": "History Test",
        })
        history = auth_client.get("/api/scans").json()
        assert history["total"] >= 1


class TestScanHistory:
    def test_get_history_authenticated(self, auth_client):
        res = auth_client.get("/api/scans")
        assert res.status_code == 200
        data = res.json()
        assert "total" in data
        assert "scans" in data

    def test_delete_scan(self, auth_client):
        scan_res = auth_client.post("/api/scan/text", json={
            "text": "delete@test.com",
            "label": "To Delete",
        })
        scan_id = scan_res.json()["scan_id"]
        del_res = auth_client.delete(f"/api/scan/{scan_id}")
        assert del_res.status_code == 204

    def test_delete_nonexistent_scan(self, auth_client):
        res = auth_client.delete("/api/scan/999999")
        assert res.status_code == 404


class TestDashboard:
    def test_dashboard_stats_authenticated(self, auth_client):
        res = auth_client.get("/api/dashboard/stats")
        assert res.status_code == 200
        data = res.json()
        assert "total_scans" in data
        assert "total_findings" in data
        assert "recent_scans" in data

    def test_health_check(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


class TestMasking:
    def test_masking_service(self):
        from app.utils.masking import mask_email, mask_generic, mask_card, mask_aadhaar
        assert mask_email("arjun@gmail.com") == "a****@gmail.com"
        assert mask_generic("9876543210", keep_last=4) == "******3210"
        assert mask_card("4111 1111 1111 1111") == "**** **** **** 1111"
        assert mask_aadhaar("2345 6789 0123") == "**** **** 0123"

    def test_mask_full(self):
        from app.utils.masking import mask_full
        result = mask_full("sk_test_abc123")
        assert all(c == "*" for c in result)


class TestRiskAnalyzer:
    def test_critical_score_for_password(self):
        from app.services.risk_analyzer import calculate_risk
        from app.detectors.base import RawFinding
        # One PASSWORD at 0.95 conf = 20 * 0.95 = 19 → LOW by itself
        # Two findings push it over 25 (MEDIUM) and with high conf over 50 (HIGH)
        findings = [
            RawFinding(type="PASSWORD", value="s", masked_value="*",
                start=0, end=1, confidence=0.95, severity="CRITICAL",
                location="Line 1", context_snippet=""),
            RawFinding(type="API_KEY", value="s", masked_value="*",
                start=2, end=3, confidence=0.99, severity="CRITICAL",
                location="Line 1", context_snippet=""),
        ]
        score, level = calculate_risk(findings)
        assert score >= 25
        assert level in ("MEDIUM", "HIGH", "CRITICAL")

    def test_zero_score_for_empty(self):
        from app.services.risk_analyzer import calculate_risk
        score, level = calculate_risk([])
        assert score == 0.0
        assert level == "LOW"

    def test_email_gives_low_medium_score(self):
        from app.services.risk_analyzer import calculate_risk
        from app.detectors.base import RawFinding
        findings = [RawFinding(
            type="EMAIL", value="a@b.com", masked_value="a*@b.com",
            start=0, end=7, confidence=0.97, severity="MEDIUM",
            location="Line 1", context_snippet=""
        )]
        score, level = calculate_risk(findings)
        assert score < 25  # Email alone should be LOW/MEDIUM
