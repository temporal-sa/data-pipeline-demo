from flask import Flask, render_template, request, jsonify
import uuid
import os
import sys
from data import JobInput

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

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


@app.route('/', methods=['GET', 'POST'])
async def main_order_page():
    job_id = str(uuid.uuid4().int)[:6]

    return render_template('index.html', data=data, scenarios=scenarios, job_id=job_id)

@app.route('/run_job')
async def run_job():
    selected_scenario = request.args.get('scenario')
    job_id = request.args.get('job_id')
    client = await get_client()

    input = DataPipelineParams(
        input_filename=data['input_filename'], 
        foldername=data['foldername'],
        poll_or_wait=data['poll_or_wait'],
        validation=data['validation'],
        scenario=selected_scenario,
        key=job_id
    )         

    if selected_scenario == "HappyPath":
        await client.start_workflow(
            "DataPipelineWorkflowHappyPath",
            input,
            id=f'job-{job_id}',
            task_queue="worker_specific_task_queue-distribution-queue",
        )   
    else:
        await client.start_workflow(
            "DataPipeline"+ selected_scenario,
            input,
            id=f'job-{job_id}',
            task_queue="worker_specific_task_queue-distribution-queue",
        )       

    return render_template('job_progress.html', selected_scenario=selected_scenario, job_id=job_id)

@app.route('/confirmation')
async def order_confirmation():
    job_id = request.args.get('job_id')

    client = await get_client()
    pipeline_workflow = client.get_workflow_handle(f'job-{job_id}')
    await pipeline_workflow.result()


    return render_template('confirmation.html', job_id=job_id)

@app.route('/get_progress')
async def get_progress():
    job_id = request.args.get('job_id')

    progress_percent = 0
    try:
        client = await get_client()
        pipeline_workflow = client.get_workflow_handle(f'job-{job_id}')
        progress_percent = await pipeline_workflow.query("progress")

        desc = await pipeline_workflow.describe()
        if desc.status == 3:
            error_message = f"Workflow failed: job-{job_id}"
            print(f"Error in get_progress route: {error_message}")
            return jsonify({"error": error_message}), 500            

        return jsonify({"progress": progress_percent})
    except:
        return jsonify({"progress": progress_percent})

@app.route('/signal', methods=['POST'])
async def signal():
    job_id = request.args.get('job_id')

    try:
        client = await get_client()
        pipeline_workflow = client.get_workflow_handle(f'job-{job_id}')
        await pipeline_workflow.signal("load_complete_signal", "complete")
    except Exception as e:
        print(f"Error sending signal: {str(e)}")
        return jsonify({"error": str(e)}), 500       

    return 'Signal received successfully', 200

@app.route('/update', methods=['POST'])
async def update():
    job_id = request.args.get('job_id')

    update_result = None
    try:
        client = await get_client()
        pipeline_workflow = client.get_workflow_handle(f'job-{job_id}')
        update_result = await pipeline_workflow.execute_update(
            update="load_complete_update",
            arg="complete",
        )
    except Exception as e:
        result = f"Update for job_id {job_id} rejected, not valid! {str(e)}"
        return jsonify(result=result)

    result = f"Update for job_id {job_id} accepted: {update_result}"

    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)    
