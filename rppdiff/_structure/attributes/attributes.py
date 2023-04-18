from typing import Iterator, Optional, Protocol

from rppdiff._diff.differ import Diffable
from rppdiff.rppstr import RppStr


class Attributes(Diffable, Protocol):
    '''The base type for chunk attribute lists.

    This is a base protocol (interface) that cannot be instantiated on its own.
    Attributes are `Diffable` and `Iterable`, iterating over their string values.

    Attributes are a list of zero or more strings, which define extra information about a Chunk.
    Unlike Settings, Attributes have no "key"--they are just values.
    Since the attributes for most Chunk types have known meanings, there may be multiple concrete Attributes types.
    '''

    def __iter__(self) -> Iterator[RppStr]:
        ...

    def chunk_id(self) -> Optional[str]:
        return None
