from dataclasses import dataclass
from typing import Iterator, Self

from rppdiff._diff.differ import Diffable, Differ
from rppdiff._diff.result import DiffResult
from rppdiff._diff.seq import DiffableSequence
from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.attributes.attributes import Attributes
from rppdiff.diff import Modify
from rppdiff.rppstr import RppStr


@dataclass(frozen=True)
class KnownAttribute(Diffable):
    known_name: str
    known_val: str
    rpp_val: RppStr

    def diff(self: Self, other: Self, differ: Differ) -> DiffResult:
        if self.known_name == other.known_name:
            if self.known_val == other.known_val:
                return DiffResult()

            differ.append_modification(
                Modify(self.known_val, other.known_val), at=self.rpp_val.span)
            return DiffResult(True)

        differ.append_deletion(self.known_val, at=self.rpp_val.span)
        differ.append_insertion(other.known_val, at=other.rpp_val.span)
        return DiffResult(True)

    @property
    def span(self) -> RppSpan:
        return self.rpp_val.span

    @classmethod
    def is_same_as(cls, self: Self, other: Self) -> bool:
        return self.known_name == other.known_name

    def __str__(self) -> str:
        return f'{self.known_name}: {self.known_val}'


@dataclass(frozen=True)
class KnownAttributes(Attributes):
    attrs: DiffableSequence[KnownAttribute]
    span_: RppSpan

    def __iter__(self) -> Iterator[RppStr]:
        return map(lambda a: a.rpp_val, iter(self.attrs))

    def diff(self, other: Self, differ: Differ) -> DiffResult:
        return differ.diff(self.attrs, other.attrs)

    @property
    def span(self) -> RppSpan:
        return self.span_
