from dataclasses import dataclass
from typing import Self

from rppdiff._diff.differ import Diffable, Differ
from rppdiff._diff.result import DiffResult
from rppdiff._parser.rppspan import RppSpan
from rppdiff._parser.scan import Token
from rppdiff.diff import Modify


@dataclass(frozen=True)
class RppStr(Diffable):
    value: str
    span_: RppSpan

    @classmethod
    def from_token(cls, token: Token) -> 'RppStr':
        return RppStr(token.value, token.span)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RppStr):
            return NotImplemented

        return self.value == other.value

    def diff(self, other: Self, differ: Differ) -> DiffResult:
        if self.value != other.value:
            differ.append_modification(
                Modify(self.value, other.value), at=self.span)

            return DiffResult(True)

        return DiffResult()

    @property
    def span(self) -> RppSpan:
        return self.span_
