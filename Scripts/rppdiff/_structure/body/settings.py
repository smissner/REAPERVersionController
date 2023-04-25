from typing import Iterator, Protocol, Sequence, runtime_checkable

from rppdiff._diff.differ import Diffable
from rppdiff._parser.rppspan import RppSpan
from rppdiff.rppstr import RppStr


@runtime_checkable
class Setting(Diffable, Protocol):
    @property
    def key(self) -> str:
        ...

    @property
    def values(self) -> Sequence[RppStr]:
        ...

    @property
    def span(self) -> RppSpan:
        ...


class Settings(Protocol):
    def __contains__(self, value: object) -> bool:
        ...

    def __iter__(self) -> Iterator[Setting]:
        ...

    def __len__(self) -> int:
        ...
