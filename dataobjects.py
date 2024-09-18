from dataclasses import dataclass

IDEMPOTENT_FILE = "idempotent_keys.txt"

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
    scenario: str
    key: str

class CustomException(Exception):
    """Custom exception for specific error handling."""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors
