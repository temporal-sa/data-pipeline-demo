from pathlib import Path
import random
import os
import json
import shutil
import time

from temporalio import activity
from temporalio.exceptions import ApplicationError
from dataobjects import DataPipelineParams, IDEMPOTENT_FILE

ErrorAPIUnavailable = "DataPipelineAPIFailure"

@activity.defn
async def get_available_task_queue() -> str:
    """Just a stub for typedworkflow invocation."""
    raise NotImplementedError

@activity.defn
async def validate(input: DataPipelineParams) -> bool:
    if(input.validation == "blue"):
        return False
    else:
        return True

@activity.defn
async def extract(input: DataPipelineParams) -> str:
    if err := initialize(input.foldername):
        raise ApplicationError("Initialization failed! " + err, non_retryable=True)
 
    shutil.copy(input.foldername + "/source/" + input.input_filename, input.foldername + "/working/" + input.input_filename)
    
    # Simulate random sleep
    time.sleep(random.randint(1, 3))
    activity.heartbeat(input.input_filename)

    return "success"

@activity.defn
async def transform(input: DataPipelineParams) -> str:    
    namespaces, err = get_namespaces(input.foldername, input.input_filename)
    if err:
        raise ApplicationError("Failed to load namespaces from json file! " + err, non_retryable=True)

    workingfilename = input.foldername + "/working/" + Path(input.input_filename).stem  + ".csv"
    namespacesCSVFile = open(workingfilename, "w+")
    namespacesCSVFile.write(f"Namespace,\n")
    for i in namespaces:
        namespacesCSVFile.write(f"{i},\n")
        # Simulate sleep
        time.sleep(1)
        activity.heartbeat(input.input_filename)

    namespacesCSVFile.close()
   

    return "success"

@activity.defn
async def load(input: DataPipelineParams) -> str:
    keyExists, err = is_idempotent(input.key)
    if err:
        raise ApplicationError("Failed to read idempotency key! " + err, non_retryable=True)
    elif keyExists:
        return "idempotency key " + input.key + " found, skipping... "
    
    shutil.copy(input.foldername + "/working/" + Path(input.input_filename).stem  + ".csv", input.foldername + "/output/" + Path(input.input_filename).stem  + ".csv")
    
    # Simulate random sleep
    time.sleep(random.randint(1, 3))
    activity.heartbeat(input.input_filename)

    if err := cleanup(input.foldername):
        raise ApplicationError("Cleanup failed! " + err, non_retryable=True)
    
    if err := write_idempotent_key(input.key):
        raise ApplicationError("Failed to create idempotency key! " + err, non_retryable=True)

    return "success"

# this activity simulates polling for demo purposes
# see https://community.temporal.io/t/what-is-the-best-practice-for-a-polling-activity/328/2
# it throws an exception 90% of the time (simulating "not found")
# 10% of the time it simulates "found" and returns 
@activity.defn
async def poll(input: DataPipelineParams, workflow_type: str) -> str:
    if ErrorAPIUnavailable == workflow_type:
        if activity.info().attempt < 10:
            raise Exception("Poll failed: not found")
        return "polled successfully: found"
    else:
        # Simulate delay
        time.sleep(5)
        return "polled successfully: found"

def initialize(datafolder: str):
    try:    
        if(os.path.isfile(datafolder + "/working/" + "info.json")):
            os.remove(datafolder + "/working/" + "info.json")
        if(os.path.isfile(datafolder + "/working/" + "info.csv")):
            os.remove(datafolder + "/working/" + "info.csv")
        if(os.path.isfile(datafolder + "/output/" + "info.csv")):
            os.remove(datafolder + "/output/" + "info.csv")

        os.makedirs(datafolder + "/working/", exist_ok=True)
        os.makedirs(datafolder + "/output/", exist_ok=True)
    except OSError as e:
        return str(e)

def cleanup(datafolder: str):
    try:    
        if(os.path.isfile(datafolder + "/working/" + "info.json")):
            os.remove(datafolder + "/working/" + "info.json")
        if(os.path.isfile(datafolder + "/working/" + "info.csv")):
            os.remove(datafolder + "/working/" + "info.csv")
    except OSError as e:
        return str(e)
    
def get_namespaces(datafolder: str, filename: str):
    namespaces = []
    try:
        namespacesJSONFile = open(datafolder + "/working/" + filename, "r")
        namespacesDict = json.load(namespacesJSONFile)
        namespacesJSONFile.close()

        for i in namespacesDict['namespaces']:
            namespaces.append(i)
    except OSError as e:
        return namespaces, str(e) 
    
    return namespaces, None

def is_idempotent(key):
    try: 
        if not os.path.exists(IDEMPOTENT_FILE):
            return False, None
        with open(IDEMPOTENT_FILE, "r") as file:
            keys = file.read().splitlines()
            return key in keys, None
    except OSError as e:
        return False, str(e)


def write_idempotent_key(key):
    try:
        with open(IDEMPOTENT_FILE, "a") as file:
            file.write(f"{key}\n")
    except OSError as e:
        return str(e)