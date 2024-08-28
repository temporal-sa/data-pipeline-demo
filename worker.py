import asyncio
import random
from random import randint
from uuid import UUID

from temporalio import activity
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

interrupt_event = asyncio.Event()

logging.basicConfig(level=logging.INFO)

async def main():
    client = await get_client()

    random.seed(randint(100, 999))

    # Create random task queues and build task queue selection function
    task_queue: str = f"activity_sticky_queue-host-{UUID(int=random.getrandbits(128))}"

    # Randomly assign job to a task queue
    @activity.defn(name="get_available_task_queue")
    async def get_task_queue() -> str:
        return task_queue

    run_futures = []
    handle = Worker(
        client,
        task_queue="activity_sticky_queue-distribution-queue",
        workflows=[DataPipelineWorkflowHappyPath, DataPipelineWorkflowAdvancedVisibility, DataPipelineWorkflowAPIFailure, DataPipelineWorkflowNonRecoverableFailure, DataPipelineWorkflowRecoverableFailure, DataPipelineWorkflowHumanInLoopSignal, DataPipelineWorkflowHumanInLoopUpdate], 
        activities=[get_task_queue, validate, extract, transform, load, poll, poll_with_failure],
    )
    run_futures.append(handle.run())
    print("Base worker started")

    print(f"Worker {task_queue} started")
    print("All workers started, ctrl+c to exit")

    # Wait until interrupted
    await asyncio.gather(*run_futures)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        interrupt_event.set()
        loop.run_until_complete(loop.shutdown_asyncgens())
        print("\nShutting down workers")