"""
Unit tests for actions/send_email.py
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.actions.send_email import send_email_action


@pytest.mark.asyncio
async def test_send_email_action_delegates_correctly():
    """Test that send_email_action properly delegates to email_utils.send_email."""
    recipients = ["test@example.com"]
    subject = "Test Subject"
    body = "Test Body"
    api_key = "test_api_key"
    from_email = "sender@example.com"
    expected_result = "Email sent successfully to 1 recipients"

    # Mock email_utils.send_email
    with patch(
        "src.actions.send_email.email.send_email", new_callable=AsyncMock
    ) as mock_send_email:
        mock_send_email.return_value = expected_result

        result = await send_email_action(
            recipients=recipients,
            subject=subject,
            body=body,
            postmark_api_key=api_key,
            sender_email=from_email,
        )

        # Verify the delegation
        mock_send_email.assert_called_once_with(
            recipients=recipients,
            subject=subject,
            body=body,
            api_key=api_key,
            from_email=from_email,
        )

        assert result == expected_result


@pytest.mark.asyncio
async def test_send_email_action_propagates_exceptions():
    """Test that send_email_action propagates exceptions from email_utils.send_email."""
    recipients = ["test@example.com"]
    subject = "Test Subject"
    body = "Test Body"

    with patch(
        "src.actions.send_email.email.send_email", new_callable=AsyncMock
    ) as mock_send_email:
        mock_send_email.side_effect = ValueError("No valid email addresses provided")

        with pytest.raises(ValueError) as exc_info:
            await send_email_action(
                recipients=recipients,
                subject=subject,
                body=body,
                postmark_api_key="test_key",
                sender_email="sender@example.com",
            )

        assert "No valid email addresses provided" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_email_action_extracts_kwargs():
    """Test that send_email_action correctly extracts api_key and from_email from kwargs."""
    recipients = ["test@example.com"]
    subject = "Test Subject"
    body = "Test Body"

    with patch(
        "src.actions.send_email.email.send_email", new_callable=AsyncMock
    ) as mock_send_email:
        mock_send_email.return_value = "Success"

        await send_email_action(
            recipients=recipients,
            subject=subject,
            body=body,
            postmark_api_key="extracted_api_key",
            sender_email="extracted@sender.com",
        )

        # Verify only the expected arguments were passed
        mock_send_email.assert_called_once_with(
            recipients=recipients,
            subject=subject,
            body=body,
            api_key="extracted_api_key",
            from_email="extracted@sender.com",
        )
