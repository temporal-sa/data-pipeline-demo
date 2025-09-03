import uuid

from flask import Flask, jsonify, render_template, request
from flask.wrappers import Response

from client import get_client
from dataobjects import DataPipelineParams

app = Flask(__name__)

# Scenario choices dropdown
scenarios = [
    "HappyPath",
    "AdvancedVisibility",
    "HumanInLoopSignal",
    "HumanInLoopUpdate",
    "Idempotency",
    "APIFailure",
    "RecoverableFailure",
    "NonRecoverableFailure",
]

data = {
    "input_filename": "info.json",
    "foldername": "./demodata",
    "poll_or_wait": "poll",
    "validation": "orange",
}


@app.route("/", methods=["GET", "POST"])
async def main_order_page() -> str:
    job_id = str(uuid.uuid4().int)[:6]

    return render_template("index.html", data=data, scenarios=scenarios, job_id=job_id)


@app.route("/run_job")
async def run_job() -> str | tuple[str, int]:
    selected_scenario = request.args.get("scenario")
    job_id = request.args.get("job_id")

    if not selected_scenario:
        return "Error: scenario parameter is required", 400
    if not job_id:
        return "Error: job_id parameter is required", 400

    client = await get_client()

    input = DataPipelineParams(
        input_filename=data["input_filename"],
        foldername=data["foldername"],
        poll_or_wait=data["poll_or_wait"],
        validation=data["validation"],
        scenario=selected_scenario,
        key=job_id,
    )

    if selected_scenario == "HappyPath":
        await client.start_workflow(
            "DataPipelineWorkflowHappyPath",
            input,
            id=f"job-{job_id}",
            task_queue="worker_specific_task_queue-distribution-queue",
        )
    else:
        await client.start_workflow(
            "DataPipeline" + selected_scenario,
            input,
            id=f"job-{job_id}",
            task_queue="worker_specific_task_queue-distribution-queue",
        )

    return render_template("job_progress.html", selected_scenario=selected_scenario, job_id=job_id)


@app.route("/confirmation")
async def order_confirmation() -> str | tuple[str, int]:
    job_id = request.args.get("job_id")

    if not job_id:
        return "Error: job_id parameter is required", 400

    client = await get_client()
    pipeline_workflow = client.get_workflow_handle(f"job-{job_id}")
    await pipeline_workflow.result()

    return render_template("confirmation.html", job_id=job_id)


@app.route("/get_progress")
async def get_progress() -> Response | tuple[Response, int]:
    job_id = request.args.get("job_id")

    if not job_id:
        return jsonify({"error": "job_id parameter is required"}), 400

    progress_percent = 0
    try:
        client = await get_client()
        pipeline_workflow = client.get_workflow_handle(f"job-{job_id}")

        try:
            progress_percent = await pipeline_workflow.query("progress")
        except Exception as e:
            print(e)

        desc = await pipeline_workflow.describe()
        if desc.status == 3:
            error_message = f"Workflow failed: job-{job_id}"
            print(f"Error in get_progress route: {error_message}")
            return jsonify({"error": error_message}), 500

        return jsonify({"progress": progress_percent})
    except Exception:
        return jsonify({"progress": progress_percent})


@app.route("/signal", methods=["POST"])
async def signal() -> tuple[str, int] | tuple[Response, int]:
    job_id = request.args.get("job_id")

    if not job_id:
        return jsonify({"error": "job_id parameter is required"}), 400

    try:
        client = await get_client()
        pipeline_workflow = client.get_workflow_handle(f"job-{job_id}")
        await pipeline_workflow.signal("load_complete_signal", "complete")
    except Exception as e:
        print(f"Error sending signal: {str(e)}")
        return jsonify({"error": str(e)}), 500

    return "Signal received successfully", 200


@app.route("/update", methods=["POST"])
async def update() -> Response:
    job_id = request.args.get("job_id")

    if not job_id:
        return jsonify({"error": "job_id parameter is required"})

    update_result = None
    try:
        client = await get_client()
        pipeline_workflow = client.get_workflow_handle(f"job-{job_id}")
        update_result = await pipeline_workflow.execute_update(
            update="load_complete_update",
            arg="complete",
        )
    except Exception as e:
        result = f"Update for job_id {job_id} rejected, not valid! {str(e)}"
        return jsonify(result=result)

    result = f"Update for job_id {job_id} accepted: {update_result}"

    return jsonify(result=result)


if __name__ == "__main__":
    app.run(debug=True)
