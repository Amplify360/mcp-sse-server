"""
Simple email utilities for the MCP server reference implementation.
"""

import logging
import re
import smtplib
from email.message import EmailMessage
from typing import List, Tuple

logger = logging.getLogger(__name__)


def _validate_email_addresses(email_list: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate email addresses using regex pattern.

    Args:
        email_list: List of email addresses to validate

    Returns:
        Tuple of (valid_emails, invalid_emails)
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    valid_emails = []
    invalid_emails = []

    for email in email_list:
        if not email:
            continue

        email = email.strip()
        if not email:
            continue

        if re.match(email_pattern, email):
            valid_emails.append(email)
        else:
            invalid_emails.append(email)
            logger.warning(f"Invalid email address format: {email}")

    return valid_emails, invalid_emails


async def send_email(
    recipients: List[str], subject: str, body: str, api_key: str, from_email: str
) -> str:
    """
    Send a simple email to the specified recipients.

    Args:
        recipients: List of email addresses to send to
        subject: Email subject line
        body: Email body content
        api_key: Postmark API key for authentication
        from_email: Sender email address

    Returns:
        Success message with recipient count

    Raises:
        ValueError: If no valid recipients provided
        Exception: If email sending fails
    """
    if not recipients:
        raise ValueError("No valid email addresses provided")

    logger.info(f"Sending email to {len(recipients)} recipients")

    # Validate email addresses
    valid_emails, invalid_emails = _validate_email_addresses(recipients)

    if invalid_emails:
        logger.warning(f"Skipping {len(invalid_emails)} invalid email addresses")

    if not valid_emails:
        raise ValueError("No valid email addresses provided")

    # Create email message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(valid_emails)
    msg.set_content(body)

    # Send email via SMTP
    try:
        logger.info("Connecting to Postmark SMTP server")
        with smtplib.SMTP("smtp.postmarkapp.com", 587) as server:
            server.starttls()
            # NOTE: Postmark requires the API key as both username and password
            # This is Postmark's recommended authentication pattern
            # SECURITY: API key should be stored in Azure Key Vault or secure env vars, never committed
            server.login(api_key, api_key)
            server.send_message(msg)

        success_msg = f"Email sent successfully to {len(valid_emails)} recipients"
        logger.info(success_msg)
        return success_msg

    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise Exception(error_msg) from e
