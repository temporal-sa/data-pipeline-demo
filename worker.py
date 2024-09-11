import asyncio
import random
from random import randint
from uuid import UUID

from temporalio import activity
from temporalio.worker import Worker
from activities import extract, validate, transform, load, poll
from DataPipelineWorkflowHappyPath import DataPipelineWorkflowHappyPath
from DataPipelineWorkflowScenarios import DataPipelineWorkflowScenarios

from client import get_client

import logging

interrupt_event = asyncio.Event()

async def main():
    logging.basicConfig(level=logging.INFO)

    # Comment line to see non-deterministic functionality
    random.seed(667)

    # Create random task queues and build task queue selection function
    task_queue: str = (
        f"worker_specific_task_queue-host-{UUID(int=random.getrandbits(128))}"
    )

    @activity.defn(name="get_available_task_queue")
    async def select_task_queue() -> str:
        """Randomly assign the job to a queue"""
        return task_queue

    # Start client
    client = await get_client()

    # Run a worker to distribute the workflows
    run_futures = []
    handle = Worker(
        client,
        task_queue="worker_specific_task_queue-distribution-queue",
        workflows=[
            DataPipelineWorkflowHappyPath, 
            DataPipelineWorkflowScenarios
        ],
        activities=[select_task_queue, validate],
    )
    run_futures.append(handle.run())
    print("Base worker started")

    # Run unique task queue for this particular host
    handle = Worker(
        client,
        task_queue=task_queue,
        activities=[
            extract, 
            transform, 
            load, 
            poll, 
        ],
    )
    run_futures.append(handle.run())
    # Wait until interrupted
    print(f"Worker {task_queue} started")

    print("All workers started, ctrl+c to exit")
    await asyncio.gather(*run_futures)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        interrupt_event.set()
        loop.run_until_complete(loop.shutdown_asyncgens())
        print("\nShutting down workers")