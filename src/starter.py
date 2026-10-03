import asyncio
from temporalio.client import Client

from emailing_service_temporal.workflows import OnboardingParams, OnboardingWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    user_id = "user_456"
    workflow_id = f"onboarding-{user_id}"

    # 1. Start the workflow (Deduplicated by workflow_id)
    handle = await client.start_workflow(
        OnboardingWorkflow.run,
        OnboardingParams(user_id=user_id, email="user456@example.com"),
        id=workflow_id,
        task_queue="email-drip-queue",
    )

    # 2. Query the internal workflow state
    status = await handle.query(OnboardingWorkflow.get_status)
    print(f"Workflow status: {status}")

    # Optional: Test sending an unsubscribe signal
    # await handle.signal(OnboardingWorkflow.unsubscribe)
    # print("Unsubscribe signal sent!")

    # 3. Wait for the workflow result
    result = await handle.result()
    print(f"Workflow finished with result: '{result}'")

if __name__ == "__main__":
    asyncio.run(main())

    