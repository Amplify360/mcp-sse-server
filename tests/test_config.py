"""
Unit tests for config.py
"""

import os
from unittest.mock import patch

import pytest

from src.config import load_config


def test_load_config_success():
    """Test successful config loading with all required environment variables."""
    with patch.dict(
        os.environ,
        {
            "MCP_SERVER_AUTH_KEY": "test_auth_key",
            "POSTMARK_API_KEY": "test_postmark_key",
            "SENDER_EMAIL": "test@example.com",
        },
    ):
        config = load_config()

        assert config.MCP_SERVER_AUTH_KEY == "test_auth_key"
        assert config.POSTMARK_API_KEY == "test_postmark_key"
        assert config.SENDER_EMAIL == "test@example.com"
        assert config.LOG_LEVEL == "DEBUG"  # default value
        assert config.ENVIRONMENT == "development"  # default value


def test_load_config_missing_required_key():
    """Test config validation fails when required environment variables are missing."""
    # Override system env vars by setting them to empty string, which should be treated as missing
    with patch.dict(
        os.environ,
        {
            "MCP_SERVER_AUTH_KEY": "test_key",
            "POSTMARK_API_KEY": "test_postmark",
            "SENDER_EMAIL": "",  # Empty string should be treated as missing
        },
        clear=True,
    ):
        with patch("src.config.load_dotenv"):
            with pytest.raises(ValueError) as exc_info:
                load_config()

            assert "Missing required configuration" in str(exc_info.value)
            assert "SENDER_EMAIL" in str(exc_info.value)


def test_load_config_empty_required_key():
    """Test config loading fails when required environment variables are empty strings."""
    with patch.dict(
        os.environ,
        {
            "MCP_SERVER_AUTH_KEY": "test_auth_key",
            "POSTMARK_API_KEY": "",  # Empty string should be treated as missing
            "SENDER_EMAIL": "test@example.com",
        },
    ):
        with patch("src.config.load_dotenv"):
            with pytest.raises(ValueError) as exc_info:
                load_config()

            assert "Missing required configuration" in str(exc_info.value)
            assert "POSTMARK_API_KEY" in str(exc_info.value)


def test_load_config_validates_all_missing_keys():
    """Test that all missing required keys are reported in the error message."""
    with patch.dict(
        os.environ,
        {
            # All required keys missing/empty
            "MCP_SERVER_AUTH_KEY": "",
            "POSTMARK_API_KEY": "",
            "SENDER_EMAIL": "",
        },
        clear=True,
    ):
        with patch("src.config.load_dotenv"):
            with pytest.raises(ValueError) as exc_info:
                load_config()

            error_msg = str(exc_info.value)
            assert "Missing required configuration" in error_msg
            assert "MCP_SERVER_AUTH_KEY" in error_msg
            assert "POSTMARK_API_KEY" in error_msg
            assert "SENDER_EMAIL" in error_msg
