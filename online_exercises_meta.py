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
    # short name for naming files
    shortname: str
    # long name for showing user
    name: str
    # folder with source audio
    folder: str
    # way that sets should be titled (eg. chapters or lessons)
    set_prefix: str


COLLECTIONS: Mapping[str, CollectionMeta] = {
    "ssw": CollectionMeta(
        id="SEE_SAY_WRITE",
        name="See Say Write",
        shortname="ssw",
        folder="see-say-write",
        set_prefix="Lessons",
    ),
    "walc-1": CollectionMeta(
        id="WALC1",
        name="We Are Learning Cherokee 1",
        shortname="walc-1",
        folder="walc-1",
        set_prefix="Chapter",
    ),
}
