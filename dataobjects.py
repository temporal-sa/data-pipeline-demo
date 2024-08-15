from dataclasses import dataclass


@dataclass
class YourParams:
    greeting: str
    name: str


@dataclass
class DataPipelineParams:
    input_filename: str 
    poll_or_wait: str
    foldername: str #this would be a reference to a network folder in  real example
    validation: str
