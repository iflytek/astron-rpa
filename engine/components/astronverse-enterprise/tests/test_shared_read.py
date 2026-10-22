from unittest.mock import Mock

import pytest
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


@pytest.mark.parametrize("value", [{}, {"subVarList": []}])
def test_empty_shared_variable_groups_return_no_value(monkeypatch, value):
    monkeypatch.setattr(enterprise, "get_remote_var_value", lambda _: value)
    assert enterprise.Enterprise.get_shared_variable("fixture") is None


@pytest.mark.parametrize("include_plaintext", [False, True])
def test_encrypted_and_mixed_groups_use_current_enterprise_interface(monkeypatch, include_plaintext):
    cipher = Mock()
    cipher.decrypt.return_value = "decrypted-value"
    constructor = Mock(return_value=cipher)
    key = Mock(return_value="synthetic-key")
    entries = [{"varName": "secret", "varValue": "encrypted-value", "encrypt": True}]
    if include_plaintext:
        entries.append({"varName": "plain", "varValue": 0, "encrypt": False})
    monkeypatch.setattr(enterprise, "Ciphertext", constructor)
    monkeypatch.setattr(enterprise, "get_remote_var_key", key)
    monkeypatch.setattr(enterprise, "get_remote_var_value", lambda _: {"subVarList": entries})
    expected = {"secret": "decrypted-value"}
    if include_plaintext:
        expected["plain"] = 0
    assert enterprise.Enterprise.get_shared_variable("fixture") == expected
    constructor.assert_called_once_with("encrypted-value")
    cipher.set_key.assert_called_once_with("synthetic-key")
    cipher.decrypt.assert_called_once_with()
    key.assert_called_once_with()
