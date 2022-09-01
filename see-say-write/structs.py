from dataclasses import dataclass

@dataclass
class SplitMetadata:
    source_file: str
    out_file: str
    start: int
    end: int
