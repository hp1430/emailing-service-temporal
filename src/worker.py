import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from emailing_service_temporal.activities import check_user_profile_completed, send_email
from emailing_service_temporal.workflows import OnboardingWorkflow

TASK_QUEUE_NAME = "email-drip-queue"

async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        workflows=[OnboardingWorkflow],
        activities=[send_email, check_user_profile_completed],
    )

    print(f"Worker started. Listening on task queue: '{TASK_QUEUE_NAME}'...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())