import asyncio
import os

from temporalio.worker import Worker
from activities import extract, validate, transform, load, poll, poll_with_failure
from DataPipelineWorkflowHappyPath import DataPipelineWorkflowHappyPath
from DataPipelineWorkflowAdvancedVisibility import DataPipelineWorkflowAdvancedVisibility
from DataPipelineWorkflowAPIFailure import DataPipelineWorkflowAPIFailure
from DataPipelineWorkflowNonRecoverableFailure import DataPipelineWorkflowNonRecoverableFailure
from DataPipelineWorkflowRecoverableFailure import DataPipelineWorkflowRecoverableFailure
from DataPipelineWorkflowHumanInLoopSignal import DataPipelineWorkflowHumanInLoopSignal
from DataPipelineWorkflowHumanInLoopUpdate import DataPipelineWorkflowHumanInLoopUpdate
from client import get_client

import logging

logging.basicConfig(level=logging.INFO)

async def main():
    client = await get_client()
    worker = Worker(
        client,
        task_queue=os.getenv("TEMPORAL_TASK_QUEUE"),
        workflows=[DataPipelineWorkflowHappyPath, DataPipelineWorkflowAdvancedVisibility, DataPipelineWorkflowAPIFailure, DataPipelineWorkflowNonRecoverableFailure, DataPipelineWorkflowRecoverableFailure, DataPipelineWorkflowHumanInLoopSignal, DataPipelineWorkflowHumanInLoopUpdate], 
        activities=[extract, validate, transform, load, poll, poll_with_failure],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
