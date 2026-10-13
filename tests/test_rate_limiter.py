from services import rate_limiter


def test_blocks_at_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(rate_limiter, "F", tmp_path / "quota.json")
    monkeypatch.setattr(rate_limiter, "LIMIT", 3)
    assert [rate_limiter.allow() for _ in range(4)] == [True, True, True, False]