import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError

with workflow.unsafe.imports_passed_through():
    from activities import extract, validate, transform, load, poll
    from dataobjects import DataPipelineParams, CustomException

@workflow.defn
class DataPipelineWorkflowRecoverableFailure:
    
    def __init__(self) -> None:
        self._progress = 0

    @workflow.run
    async def run(self, input: DataPipelineParams) -> str:
        workflow.logger.info(f"The data pipeline for {input} beginning.")
        
        # Set progress to 10%
        self._progress = 10

        # Sleep 2 seconds
        await asyncio.sleep(2)

        validation = await workflow.execute_activity(
            validate, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        if validation == False:
            workflow.logger.info(f"Validation rejected for: {input.input_filename}")
            
            raise ApplicationError(f"Workflow failed due to validation") from CustomException("Validation Failed")    

        # Set progress to 20%
        self._progress = 20

        activity_output = await workflow.execute_activity(
            extract, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        workflow.logger.info(f"Extract status: {input.input_filename}: {activity_output}")

        # Set progress to 40%
        self._progress = 40

        activity_output = await workflow.execute_activity(
            transform, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        workflow.logger.info(f"Transform status: {input.input_filename}: {activity_output}")

        # Comment out to fix recoverable scenario
        #raise Exception("Workflow bug!")

        # Set progress to 60%
        self._progress = 60

        activity_output = await workflow.execute_activity(
            load, input, start_to_close_timeout=timedelta(seconds=300), heartbeat_timeout=timedelta(seconds=20)
        )
        workflow.logger.info(f"Load status: {input.input_filename}: {activity_output}")

        # Set progress to 80%
        self._progress = 80

        # it's ok if this activity fails: it is polling every 2 seconds
        # see https://community.temporal.io/t/what-is-the-best-practice-for-a-polling-activity/328/2
        activity_output = await workflow.execute_activity(
            poll, input, start_to_close_timeout=timedelta(seconds=3000), heartbeat_timeout=timedelta(seconds=20), 
            retry_policy=RetryPolicy(initial_interval=timedelta(seconds=2), backoff_coefficient=1)
        )

        workflow.logger.info(f"Poll status: {input.input_filename}: {activity_output}")

        # Set progress to 100%
        self._progress = 100        

        return f"Successfully processed: {input.input_filename}!"

    @workflow.query
    def progress(self) -> int:
        return self._progress