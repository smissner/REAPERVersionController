from dataclasses import dataclass
from typing import Iterator, Self

from rppdiff._diff.differ import Differ
from rppdiff._diff.result import DiffResult
from rppdiff._diff.seq import DiffableSequence
from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.attributes.attributes import Attributes
from rppdiff.rppstr import RppStr


@dataclass(frozen=True)
class GenericAttributes(Attributes):
    attributes: DiffableSequence[RppStr]

    def __iter__(self) -> Iterator[RppStr]:
        return iter(self.attributes)

    def diff(self: Self, other: Self, differ: Differ) -> DiffResult:
        return differ.diff(self.attributes, other.attributes)

    @property
    def span(self) -> RppSpan:
        return self.attributes.span
