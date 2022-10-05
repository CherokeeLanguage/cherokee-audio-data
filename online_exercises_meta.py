from dataclasses import dataclass
from typing import Mapping

@dataclass
class SplitMetadata:
    """
    Metadata on where a segment was pulled out of a longer source file.
    """
    source_file: str
    out_file: str
    start: int
    end: int

@dataclass
class CollectionMeta:
    id: str
    shortname: str
    name: str
    folder: str

COLLECTIONS: Mapping[str, CollectionMeta] = {
    "ssw": CollectionMeta(
        id="SEE_SAY_WRITE",
        name="See Say Write",
        shortname="ssw",
        folder="see-say-write"
    )
}