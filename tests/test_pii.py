from app.logging_config import scrub_event
from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_passport_without_corrupting_correlation_id() -> None:
    correlation_id = "req-a1234567"

    for passport in ("B1234567", "b1234567"):
        out = scrub_text(f"Passport: {passport}")
        assert passport not in out
        assert "REDACTED_PASSPORT" in out
    assert scrub_text(correlation_id) == correlation_id


def test_scrub_full_vietnamese_address_segments() -> None:
    raw = "Địa chỉ: 123 Đường Láng, Phường Láng Hạ, Quận Đống Đa"
    out = scrub_text(raw)

    assert "Đường Láng" not in out
    assert "Phường Láng Hạ" not in out
    assert "Quận Đống Đa" not in out
    assert out.count("REDACTED_ADDRESS_VN") == 3


def test_scrub_additional_vietnamese_address_keywords() -> None:
    raw = "Xã Tân Lập, Ngõ 12 Phố Huế, Thôn Đông"
    out = scrub_text(raw)

    assert "Tân Lập" not in out
    assert "Phố Huế" not in out
    assert "Thôn Đông" not in out
    assert out.count("REDACTED_ADDRESS_VN") == 3


def test_address_pattern_does_not_scrub_technical_phrases() -> None:
    raw = "p value is 0.05; q value is high; số lượng token là 10"

    assert scrub_text(raw) == raw


def test_scrub_event_recurses_through_all_log_fields() -> None:
    event = {
        "event": "request_failed",
        "correlation_id": "req-a1234567",
        "session_id": "student@example.com",
        "payload": {
            "student@example.com": {"card": "4111 1111 1111 1111"},
            "items": ["090 123 4567", ("B1234567",)],
        },
        "exception": "Contact student@example.com",
    }

    out = scrub_event(None, "error", event)
    rendered = repr(out)

    assert out["correlation_id"] == "req-a1234567"
    assert "student@example.com" not in rendered
    assert "4111 1111 1111 1111" not in rendered
    assert "090 123 4567" not in rendered
    assert "B1234567" not in rendered
