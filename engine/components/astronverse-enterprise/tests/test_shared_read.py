from unittest.mock import Mock

from astronverse.enterprise import enterprise


def test_plain_shared_read_does_not_request_an_encryption_key(monkeypatch):
    key = Mock(side_effect=AssertionError("plaintext must not request a key"))
    monkeypatch.setattr(enterprise, "get_remote_var_key", key)
    monkeypatch.setattr(
        enterprise,
        "get_remote_var_value",
        lambda _: {"subVarList": [{"varName": "answer", "varValue": "42", "encrypt": False}]},
    )
    assert enterprise.Enterprise.get_shared_variable("fixture") == {"answer": "42"}
    key.assert_not_called()


def test_unavailable_shared_variable_returns_no_value(monkeypatch):
    monkeypatch.setattr(enterprise, "get_remote_var_value", lambda _: None)
    assert enterprise.Enterprise.get_shared_variable("missing") is None
