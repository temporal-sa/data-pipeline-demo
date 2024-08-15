import asyncio
from datetime import timedelta

from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleIntervalSpec,
    ScheduleSpec,
    ScheduleState,
)
from data_pipeline_workflows import DataPipelineWorkflow

from dataobjects import DataPipelineParams


async def main():
    client = await Client.connect("localhost:7233")

    handle = client.get_workflow_handle(workflow_id="datapipe-workflow")

    await handle.signal(DataPipelineWorkflow.load_complete, "complete")
    # Wait and return result
    result = await handle.result()
    print(f"Result: {result}")
    return result

if __name__ == "__main__":
    asyncio.run(main())
