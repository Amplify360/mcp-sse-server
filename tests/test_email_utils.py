"""
Unit tests for email_utils.py
"""

import smtplib
from unittest.mock import MagicMock, patch

import pytest

from src.utils.email import _validate_email_addresses, send_email


def test_validate_email_addresses():
    """Test email address validation with mixed valid and invalid addresses."""
    email_list = [
        "valid@example.com",
        "also.valid@test.org",
        "invalid-email",
        "missing@domain",
        "",
        "   ",
        "user@domain.co.uk",
        "@nodomain.com",
        "spaces in@email.com",
    ]

    valid_emails, invalid_emails = _validate_email_addresses(email_list)

    assert valid_emails == [
        "valid@example.com",
        "also.valid@test.org",
        "user@domain.co.uk",
    ]

    assert invalid_emails == [
        "invalid-email",
        "missing@domain",
        "@nodomain.com",
        "spaces in@email.com",
    ]


def test_validate_email_addresses_empty_list():
    """Test email validation with empty list."""
    valid_emails, invalid_emails = _validate_email_addresses([])

    assert valid_emails == []
    assert invalid_emails == []


@pytest.mark.asyncio
async def test_send_email_success():
    """Test successful email sending with mocked SMTP."""
    recipients = ["test1@example.com", "test2@example.com"]
    subject = "Test Subject"
    body = "Test Body"
    api_key = "test_api_key"
    from_email = "sender@example.com"

    # Mock the SMTP server
    mock_server = MagicMock()
    mock_server.__enter__ = MagicMock(return_value=mock_server)
    mock_server.__exit__ = MagicMock(return_value=None)

    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.return_value = mock_server

        result = await send_email(recipients, subject, body, api_key, from_email)

        # Verify SMTP was called correctly
        mock_smtp.assert_called_once_with("smtp.postmarkapp.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(api_key, api_key)
        mock_server.send_message.assert_called_once()

        assert result == "Email sent successfully to 2 recipients"


@pytest.mark.asyncio
async def test_send_email_no_valid_recipients():
    """Test send_email fails when no valid recipients provided."""
    with pytest.raises(ValueError) as exc_info:
        await send_email([], "Subject", "Body", "api_key", "from@example.com")

    assert "No valid email addresses provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_email_only_invalid_recipients():
    """Test send_email fails when only invalid recipients provided."""
    invalid_recipients = ["invalid-email", "@nodomain.com"]

    with pytest.raises(ValueError) as exc_info:
        await send_email(
            invalid_recipients, "Subject", "Body", "api_key", "from@example.com"
        )

    assert "No valid email addresses provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_email_smtp_failure():
    """Test send_email handles SMTP failures gracefully."""
    recipients = ["test@example.com"]

    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")

        with pytest.raises(Exception) as exc_info:
            await send_email(
                recipients, "Subject", "Body", "api_key", "from@example.com"
            )

        assert "Failed to send email" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_email_filters_invalid_addresses():
    """Test send_email filters out invalid addresses but continues with valid ones."""
    recipients = ["valid@example.com", "invalid-email", "also.valid@test.org"]

    # Mock the SMTP server
    mock_server = MagicMock()
    mock_server.__enter__ = MagicMock(return_value=mock_server)
    mock_server.__exit__ = MagicMock(return_value=None)

    with patch("smtplib.SMTP") as mock_smtp:
        mock_smtp.return_value = mock_server

        result = await send_email(
            recipients, "Subject", "Body", "api_key", "from@example.com"
        )

        # Should succeed with 2 valid recipients (filtered out invalid-email)
        assert result == "Email sent successfully to 2 recipients"
        mock_server.send_message.assert_called_once()
