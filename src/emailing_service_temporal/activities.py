import asyncio
from dataclasses import dataclass
from temporalio import activity


@dataclass
class EmailPayload:
    to_email: str
    template_name: str
    subject: str

@activity.defn
async def send_email(payload: EmailPayload) -> bool:
    """
    Sends an email. If this raises an exception (e.g. SMTP down, API rate limit),
    Temporal automatically retries according to the retry policy.
    """

    activity.logger.info(
        f"Sending email '{payload.subject}' ({payload.template_name}) to {payload.to_email}"
    )

    # Simulate API network call
    await asyncio.sleep(0.5)
    return True

@activity.defn
async def check_user_profile_completed(user_id: str) -> bool:
    """
    Simulates checking a relational DB to see if the user completed profile setup.
    """

    activity.logger.info(f"Checking onboarding status for user: {user_id}")
    # Simulate DB query
    await asyncio.sleep(0.5)
    return False