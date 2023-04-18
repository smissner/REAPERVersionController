from dataclasses import dataclass

from rppdiff._parser.rppspan import RppSpan
from rppdiff._parser.scan import Token
from rppdiff.rppstr import RppStr


@dataclass(frozen=True)
class BasicChunkInfo:
    kind: RppStr
    span: RppSpan

    @classmethod
    def from_parts(cls, kind: RppStr, start: Token, end: Token) -> 'BasicChunkInfo':
        span = RppSpan(start.span.start, end.span.end)
        return BasicChunkInfo(kind, span)
