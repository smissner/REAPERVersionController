from typing import Iterable, Protocol

from rppdiff._parser.elem import GenericBodyElem
from rppdiff._structure.chunk import Body


class BodyBuilder(Protocol):
    def build(self, elems: Iterable[GenericBodyElem]) -> Body:
        ...
