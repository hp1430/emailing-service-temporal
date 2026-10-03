from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from emailing_service_temporal.activities import send_email, EmailPayload, check_user_profile_completed

@dataclass
class OnboardingParams:
    user_id: str
    email: str

@workflow.defn
class OnboardingWorkflow:
    def __init__(self) -> None:
        self.unsubscribed = False

    @workflow.signal
    def unsubscribe(self) -> None:
        """
        External event sent to the running workflow (e.g., user clicks Unsubscribe).
        """
        self.unsubscribed = True

    @workflow.query
    def get_status(self) -> str:
        """
        Inspect workflow state on-the-fly without affecting execution.
        """
        if self.unsubscribed:
            return "UNSUBSCRIBED"
        return "ACTIVE"

    @workflow.run
    async def run(self, params: OnboardingParams) -> str:
        # Step1: Send welcome email immediately
        await workflow.execute_activity(
            send_email,
            EmailPayload(
                to_email=params.email,
                template_name="welcome",
                subject="Welcome to our service!",
            ),
            start_to_close_timeout=timedelta(seconds=10),
        )

        # Step 2: Durable sleep.
        # Temporal server maintains this timer. Workers consume zero resources.
        # (Use 10 seconds for demo testing; in production this would be timedelta(days=2))
        await workflow.sleep(timedelta(seconds=10))

        #check if user unsubscribed while waiting for the timer to complete
        if self.unsubscribed:
            return "Sequence terminated due to user unsubscribing."

        # Step 3: Check if user completed profile setup
        has_completed = await workflow.execute_activity(
            check_user_profile_completed,
            params.user_id,
            start_to_close_timeout=timedelta(seconds=10)
        )

        # Step 4: Conditional follow-up email
        if not has_completed and not self.unsubscribed:
            await workflow.execute_activity(
                send_email,
                EmailPayload(
                    to_email=params.email,
                    template_name="reminder",
                    subject="Reminder: Complete your profile setup!",
                ),
                start_to_close_timeout=timedelta(seconds=10)
            )
            return "Completed with reminder sent." \

        return "Completed: No reminder needed."