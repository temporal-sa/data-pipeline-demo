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
    datapipelineinput = DataPipelineParams(input_filename="info.json", 
                                           foldername="./demodata",
                                           poll_or_wait="poll",
                                           validation="orange")
    result = await client.execute_workflow(
        DataPipelineWorkflow.run, datapipelineinput, id=f"datapipe-workflow", task_queue="data-pipeline-task-queue"
    )  

    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
