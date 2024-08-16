from dataclasses import dataclass
@dataclass
class JobInput:
    JobId: str
    InputFormat: str
    OutputFormat: str
    Filename: str
    WorkDir: str
    OutputDir: str

