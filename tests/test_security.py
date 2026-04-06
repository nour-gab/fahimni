"""Unit tests for JWT utility functions."""

import pytest

from fahimni.core.security import create_access_token, decode_access_token


def test_create_and_decode_access_token_roundtrip() -> None:
    token = create_access_token(subject="11111111-1111-1111-1111-111111111111", role="PROFESSOR")
    decoded = decode_access_token(token)

    assert decoded["sub"] == "11111111-1111-1111-1111-111111111111"
    assert decoded["role"] == "PROFESSOR"


def test_decode_access_token_invalid_raises_value_error() -> None:
    with pytest.raises(ValueError):
        decode_access_token("invalid.token.value")
