from pathlib import Path
import random
import os
import json
import shutil

from temporalio import activity
from dataobjects import DataPipelineParams


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

    namespacesCSVFile.close()
   
    activity.heartbeat(input.input_filename)

    return "success"

@activity.defn
async def load(input: DataPipelineParams) -> str:
    
    shutil.copy(input.foldername + "/working/" + Path(input.input_filename).stem  + ".csv", input.foldername + "/output/" + Path(input.input_filename).stem  + ".csv")
    activity.heartbeat(input.input_filename)
    
    cleanup(input.foldername)

    return "success"

# this activity simulates polling for demo purposes
# see https://community.temporal.io/t/what-is-the-best-practice-for-a-polling-activity/328/2
# it throws an exception 90% of the time (simulating "not found")
# 10% of the time it simulates "found" and returns 
@activity.defn
async def poll_with_failure(input: DataPipelineParams) -> str:
    if random.randint(1, 10) > 9 :
        return "Poll successful: found"
    raise Exception("Poll failed: not found")

@activity.defn
async def poll(input: DataPipelineParams) -> str:
    if random.randint(1, 10) > 9 :
        return "polled successfully: found"
    raise Exception("Simulate polled: not found")

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