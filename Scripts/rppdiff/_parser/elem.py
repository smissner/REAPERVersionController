from rppdiff._structure.chunk import Chunk
from rppdiff.rppstr import RppStr


GenericBodyElem = Chunk | list[RppStr]
