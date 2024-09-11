from pathlib import Path
import random
import os
import json
import shutil
import time

from temporalio import activity
from dataobjects import DataPipelineParams

ErrorAPIUnavailable = "APIFailure"

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
    initialize(input.foldername)
    
    shutil.copy(input.foldername + "/source/" + input.input_filename, input.foldername + "/working/" + input.input_filename)
    
    # Simulate random sleep
    time.sleep(random.randint(1, 3))
    activity.heartbeat(input.input_filename)

    return "success"

@activity.defn
async def transform(input: DataPipelineParams) -> str:    
    namespaces = get_namespaces(input.foldername, input.input_filename)
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
    
    shutil.copy(input.foldername + "/working/" + Path(input.input_filename).stem  + ".csv", input.foldername + "/output/" + Path(input.input_filename).stem  + ".csv")
    
    # Simulate random sleep
    time.sleep(random.randint(1, 3))
    activity.heartbeat(input.input_filename)
    
    cleanup(input.foldername)

    return "success"

# this activity simulates polling for demo purposes
# see https://community.temporal.io/t/what-is-the-best-practice-for-a-polling-activity/328/2
# it throws an exception 90% of the time (simulating "not found")
# 10% of the time it simulates "found" and returns 
@activity.defn
async def poll(input: DataPipelineParams) -> str:
    if ErrorAPIUnavailable == input.scenario:
        if activity.info().attempt < 10:
            raise Exception("Poll failed: not found")
        return "polled successfully: found"
    else:
        # Simulate delay
        time.sleep(5)
        return "polled successfully: found"

def initialize(datafolder: str):    
    if(os.path.isfile(datafolder + "/working/" + "info.json")):
        os.remove(datafolder + "/working/" + "info.json")
    if(os.path.isfile(datafolder + "/working/" + "info.csv")):
        os.remove(datafolder + "/working/" + "info.csv")
    if(os.path.isfile(datafolder + "/output/" + "info.csv")):
        os.remove(datafolder + "/output/" + "info.csv")

def cleanup(datafolder: str):   
    if(os.path.isfile(datafolder + "/working/" + "info.json")):
        os.remove(datafolder + "/working/" + "info.json")
    if(os.path.isfile(datafolder + "/working/" + "info.csv")):
        os.remove(datafolder + "/working/" + "info.csv")


def get_namespaces(datafolder: str, filename: str):
    namespaces = []

    namespacesJSONFile = open(datafolder + "/working/" + filename, "r")
    namespacesDict = json.load(namespacesJSONFile)
    namespacesJSONFile.close()

    for i in namespacesDict['namespaces']:
        namespaces.append(i)
    return namespaces