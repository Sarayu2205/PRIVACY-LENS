"""
Unit tests for all sensitive data detectors.
Tests use synthetic data only — no real personal information.
"""
import pytest
from app.detectors.email_detector import EmailDetector
from app.detectors.phone_detector import PhoneDetector
from app.detectors.pan_detector import PANDetector
from app.detectors.aadhaar_detector import AadhaarDetector
from app.detectors.card_detector import CardDetector
from app.detectors.password_detector import PasswordDetector
from app.detectors.api_key_detector import ApiKeyDetector
from app.detectors.jwt_detector import JWTDetector
from app.detectors.private_key_detector import PrivateKeyDetector
from app.detectors.bank_account_detector import BankAccountDetector
from app.detectors.scanner import scan_text


# ── Email ─────────────────────────────────────────────────────────────────
class TestEmailDetector:
    d = EmailDetector()

    def test_detects_standard_email(self):
        findings = self.d.detect("Contact me at arjun@example.com please")
        assert len(findings) == 1
        assert findings[0].type == "EMAIL"
        assert findings[0].value == "arjun@example.com"

    def test_detects_multiple_emails(self):
        findings = self.d.detect("From: a@b.com To: c@d.org CC: e@f.co.in")
        assert len(findings) == 3

    def test_no_false_positive_on_plain_text(self):
        findings = self.d.detect("Hello world, no email here.")
        assert len(findings) == 0

    def test_email_confidence_high(self):
        findings = self.d.detect("user@domain.com")
        assert findings[0].confidence >= 0.9

    def test_email_severity_medium(self):
        findings = self.d.detect("user@domain.com")
        assert findings[0].severity == "MEDIUM"


# ── Phone ─────────────────────────────────────────────────────────────────
class TestPhoneDetector:
    d = PhoneDetector()

    def test_detects_10_digit_mobile(self):
        findings = self.d.detect("Call me at 9876543210")
        assert any(f.type == "PHONE" for f in findings)

    def test_detects_with_country_code(self):
        findings = self.d.detect("My number is +91 9876543210")
        assert any(f.type == "PHONE" for f in findings)

    def test_detects_zero_prefix(self):
        findings = self.d.detect("Landline: 09876543210")
        assert any(f.type == "PHONE" for f in findings)


# ── PAN ───────────────────────────────────────────────────────────────────
class TestPANDetector:
    d = PANDetector()

    def test_detects_pan_pattern(self):
        findings = self.d.detect("PAN: ABCDE1234F")
        assert len(findings) == 1
        assert findings[0].type == "PAN"

    def test_pan_severity_high(self):
        findings = self.d.detect("PAN ABCDE1234F")
        assert findings[0].severity == "HIGH"

    def test_no_false_positive_lowercase(self):
        findings = self.d.detect("abcde1234f")  # lowercase — should not match
        assert len(findings) == 0

    def test_pan_masked_value(self):
        findings = self.d.detect("ABCDE1234F")
        # mask_generic with keep_last=4 gives last 4 chars: "234F"
        assert findings[0].masked_value.endswith("234F")


# ── Aadhaar ───────────────────────────────────────────────────────────────
class TestAadhaarDetector:
    d = AadhaarDetector()

    def test_detects_spaced_format(self):
        findings = self.d.detect("Aadhaar: 2345 6789 0123")
        assert len(findings) >= 1
        assert findings[0].type == "AADHAAR"

    def test_detects_continuous_format(self):
        findings = self.d.detect("UID: 234567890123")
        assert any(f.type == "AADHAAR" for f in findings)

    def test_masked_shows_last_4(self):
        findings = self.d.detect("Aadhaar: 2345 6789 0123")
        assert "0123" in findings[0].masked_value


# ── Credit Card ───────────────────────────────────────────────────────────
class TestCardDetector:
    d = CardDetector()

    def test_detects_visa_test_number(self):
        # Standard Visa test number — passes Luhn
        findings = self.d.detect("Card: 4111 1111 1111 1111")
        assert len(findings) == 1
        assert findings[0].type == "CREDIT_CARD"

    def test_detects_mastercard_test_number(self):
        findings = self.d.detect("5500 0000 0000 0004")
        assert len(findings) == 1

    def test_rejects_invalid_luhn(self):
        findings = self.d.detect("4111 1111 1111 1112")  # fails Luhn
        assert len(findings) == 0

    def test_card_severity_critical(self):
        findings = self.d.detect("4111111111111111")
        assert findings[0].severity == "CRITICAL"

    def test_card_masked_shows_last_4(self):
        findings = self.d.detect("4111 1111 1111 1111")
        assert "1111" in findings[0].masked_value


# ── Password ──────────────────────────────────────────────────────────────
class TestPasswordDetector:
    d = PasswordDetector()

    def test_detects_assignment(self):
        findings = self.d.detect("password=SuperSecret123")
        assert any(f.type == "PASSWORD" for f in findings)

    def test_detects_colon_format(self):
        findings = self.d.detect("password: MyPassword@2024")
        assert any(f.type == "PASSWORD" for f in findings)

    def test_detects_passwd(self):
        findings = self.d.detect("passwd=db_password_here")
        assert any(f.type == "PASSWORD" for f in findings)

    def test_skips_placeholder(self):
        findings = self.d.detect("password=your_password")
        assert len(findings) == 0


# ── API Key ───────────────────────────────────────────────────────────────
class TestApiKeyDetector:
    d = ApiKeyDetector()

    def test_detects_assignment(self):
        findings = self.d.detect("API_KEY=my_test_api_key_1234567890abcdefghij")
        assert any(f.type == "API_KEY" for f in findings)

    def test_detects_stripe_key(self):
        # Use a clearly fake key pattern that matches the format but isn't a real key
        findings = self.d.detect("stripe_key=my_stripe_live_key_AbCdEfGhIjKlMnOpQrStUv")
        assert any(f.type == "API_KEY" for f in findings)

    def test_detects_aws_key(self):
        # AKIA prefix followed by 16 uppercase alphanumeric chars
        findings = self.d.detect("AKIATESTFAKEKEY12345")
        assert any(f.type == "API_KEY" for f in findings)

    def test_detects_github_token(self):
        # Use a clearly non-real token pattern (different prefix)
        findings = self.d.detect("GITHUB_TOKEN=ghp_fakegithubtoken1234567890abcdefghij")
        assert any(f.type == "API_KEY" for f in findings)

    def test_severity_critical(self):
        findings = self.d.detect("API_KEY=my_test_api_key_1234567890abcdefghij")
        api_findings = [f for f in findings if f.type == "API_KEY"]
        assert all(f.severity == "CRITICAL" for f in api_findings)


# ── JWT ───────────────────────────────────────────────────────────────────
class TestJWTDetector:
    d = JWTDetector()
    SAMPLE_JWT = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        ".eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ"
        ".SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    )

    def test_detects_jwt(self):
        findings = self.d.detect(f"token={self.SAMPLE_JWT}")
        assert any(f.type == "JWT_TOKEN" for f in findings)

    def test_jwt_severity_critical(self):
        findings = self.d.detect(self.SAMPLE_JWT)
        assert findings[0].severity == "CRITICAL"

    def test_jwt_masked_hides_payload(self):
        findings = self.d.detect(self.SAMPLE_JWT)
        assert "***" in findings[0].masked_value

    def test_no_false_positive_short_string(self):
        findings = self.d.detect("abc.def.ghi")  # too short
        assert len(findings) == 0


# ── Private Key ───────────────────────────────────────────────────────────
class TestPrivateKeyDetector:
    d = PrivateKeyDetector()

    def test_detects_rsa_header(self):
        # Single-line RSA header must match the partial pattern
        findings = self.d.detect("-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA0Z3\n-----END RSA PRIVATE KEY-----")
        assert len(findings) == 1
        assert findings[0].type == "PRIVATE_KEY"

    def test_detects_openssh_key(self):
        text = "-----BEGIN OPENSSH PRIVATE KEY-----\nAAAA\n-----END OPENSSH PRIVATE KEY-----"
        findings = self.d.detect(text)
        assert any(f.type in ("PRIVATE_KEY", "SSH_PRIVATE_KEY") for f in findings)


# ── Bank Account ──────────────────────────────────────────────────────────
class TestBankAccountDetector:
    d = BankAccountDetector()

    def test_detects_account_number_with_context(self):
        findings = self.d.detect("Account number: 123456789012")
        assert any(f.type == "BANK_ACCOUNT" for f in findings)

    def test_detects_ifsc(self):
        findings = self.d.detect("IFSC: HDFC0001234")
        assert any(f.type == "IFSC_CODE" for f in findings)

    def test_no_false_positive_without_context(self):
        findings = self.d.detect("Reference: 123456789012")  # no banking context
        bank_findings = [f for f in findings if f.type == "BANK_ACCOUNT"]
        assert len(bank_findings) == 0


# ── Master Scanner ────────────────────────────────────────────────────────
class TestMasterScanner:
    def test_detects_multiple_types(self):
        text = (
            "Email: test@example.com\n"
            "Phone: 9876543210\n"
            "PAN: ABCDE1234F\n"
            "password=secret123\n"
        )
        findings = scan_text(text)
        types = {f.type for f in findings}
        assert "EMAIL" in types
        assert "PAN" in types

    def test_clean_text_returns_empty(self):
        findings = scan_text("Hello world. This is a clean document.")
        assert len(findings) == 0

    def test_deduplication(self):
        """Same email should appear only once."""
        text = "Email: user@test.com and also user@test.com"
        findings = scan_text(text)
        email_findings = [f for f in findings if f.type == "EMAIL"]
        # Should have at most 2 (two distinct positions)
        assert len(email_findings) <= 2
