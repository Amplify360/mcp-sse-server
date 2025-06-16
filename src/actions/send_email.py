"""
Send email action implementation.
"""

import logging
from typing import List

from ..utils import email

logger = logging.getLogger(__name__)


async def send_email_action(
    recipients: List[str], subject: str, body: str, postmark_api_key: str, sender_email: str
) -> str:
    """
    Send a simple email to the specified recipients.

    Args:
        recipients: List of email addresses to send to
        subject: Email subject line
        body: Email body content
        postmark_api_key: Postmark API key (injected)
        sender_email: From email address (injected)

    Returns:
        Success message with recipient count
    """
    logger.info(f"Send email action called with {len(recipients)} recipients")
    try:
        result = await email.send_email(
            recipients=recipients,
            subject=subject,
            body=body,
            api_key=postmark_api_key,
            from_email=sender_email,
        )
        logger.info("Email sending completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        raise
