import logging
import asyncio
from datetime import timedelta

from temporalio import workflow

import temporalio
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import extract, validate, transform, load, poll
    from dataobjects import DataPipelineParams



@workflow.defn
class DataPipelineWorkflow:
    
    def __init__(self) -> None:
        self.load_complete = False

    @workflow.run
    async def run(self, input: DataPipelineParams) -> str:
        logging.info(f"The data pipeline for {input} beginning.")
        #   [ ] multiple files for the heartbeats?
        
        validation = await workflow.execute_activity(
            validate, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        if validation == False:
            logging.info(f"Validation rejected for: {input.input_filename}")
            return "invalidated"


        activity_output = await workflow.execute_activity(
            extract, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        logging.info(f"Extract status: {input.input_filename}: {activity_output}")


        activity_output = await workflow.execute_activity(
            transform, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        logging.info(f"Transform status: {input.input_filename}: {activity_output}")

        activity_output = await workflow.execute_activity(
            load, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        logging.info(f"Load status: {input.input_filename}: {activity_output}")

        if input.poll_or_wait == "poll":
            # it's ok if this activity fails: it is polling every 2 seconds
            # see https://community.temporal.io/t/what-is-the-best-practice-for-a-polling-activity/328/2
            activity_output = await workflow.execute_activity(
                poll, input, start_to_close_timeout=timedelta(seconds=3000), heartbeat_timeout=timedelta(seconds=20), 
                retry_policy=RetryPolicy(initial_interval=timedelta(seconds=2), backoff_coefficient=1)

            )
            logging.info(f"Poll status: {input.input_filename}: {activity_output}")
        else:
            try:
                await workflow.wait_condition(lambda: self.load_complete, timeout=45)
                logging.info(f"Received signal that load completed: {input.input_filename} load complete: {self.load_complete}")
            except asyncio.TimeoutError:
                # could return "Load did not complete before timeout."
                raise temporalio.exceptions.ApplicationError("Load did not complete before timeout")
        
        return f"Successfully processed: {input.input_filename}!"

    @workflow.signal
    async def load_complete(self, approval: str) -> None:
        self.load_complete = True