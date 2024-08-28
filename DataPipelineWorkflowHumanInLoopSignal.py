import asyncio
from datetime import timedelta

from temporalio import workflow

import temporalio
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import extract, validate, transform, load, get_available_task_queue
    from dataobjects import DataPipelineParams

@workflow.defn
class DataPipelineWorkflowHumanInLoopSignal:
    
    def __init__(self) -> None:
        self.load_complete = False
        self._progress = 0

    @workflow.run
    async def run(self, input: DataPipelineParams) -> str:
        workflow.logger.info(f"The data pipeline for {input} beginning.")

        workflow.logger.info("Searching for available worker")
        unique_worker_task_queue = await workflow.execute_activity(
            activity=get_available_task_queue,
            start_to_close_timeout=timedelta(seconds=10),
        )
        workflow.logger.info(f"Matching workflow to worker {unique_worker_task_queue}")

        # Set progress to 10%
        self._progress = 10

        # Sleep 2 seconds
        await asyncio.sleep(2)
                
        validation = await workflow.execute_activity(
            validate, 
            input,  
            start_to_close_timeout=timedelta(seconds=300), 
            heartbeat_timeout=timedelta(seconds=20)
        )
        if validation == False:
            workflow.logger.info(f"Validation rejected for: {input.input_filename}")
            return "invalidated"

        # Set progress to 20%
        self._progress = 20

        activity_output = await workflow.execute_activity(
            extract, 
            input, 
            task_queue=unique_worker_task_queue, 
            start_to_close_timeout=timedelta(seconds=300), 
            heartbeat_timeout=timedelta(seconds=20)
        )
        workflow.logger.info(f"Extract status: {input.input_filename}: {activity_output}")

        # Set progress to 40%
        self._progress = 40

        activity_output = await workflow.execute_activity(
            transform, 
            input, 
            task_queue=unique_worker_task_queue, 
            start_to_close_timeout=timedelta(seconds=300), 
            heartbeat_timeout=timedelta(seconds=20)
        )
        workflow.logger.info(f"Transform status: {input.input_filename}: {activity_output}")

        # Set progress to 60%
        self._progress = 60

        activity_output = await workflow.execute_activity(
            load, 
            input, 
            task_queue=unique_worker_task_queue, 
            start_to_close_timeout=timedelta(seconds=300), 
            heartbeat_timeout=timedelta(seconds=20)
        )
        workflow.logger.info(f"Load status: {input.input_filename}: {activity_output}")

        # Set progress to 80%
        self._progress = 80


        try:
            await workflow.wait_condition(lambda: self.load_complete, timeout=60)
            workflow.logger.info(f"Received signal that load completed: {input.input_filename} load complete: {self.load_complete}")
        except asyncio.TimeoutError:
            # could return "Load did not complete before timeout."
            raise temporalio.exceptions.ApplicationError("Load did not complete before timeout")

        # Set progress to 100%
        self._progress = 100        

        return f"Successfully processed: {input.input_filename}!"

    @workflow.signal
    async def load_complete(self, complete: str) -> None:
        self.load_complete = True

    @workflow.query
    def progress(self) -> int:
        return self._progress