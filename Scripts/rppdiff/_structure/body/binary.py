from dataclasses import dataclass
from typing import Iterator, Sequence

from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.body.settings import Setting, Settings
from rppdiff.rppstr import RppStr


@dataclass(frozen=True)
class BinarySettingLine(Setting):
    data: RppStr

    @property
    def key(self) -> str:
        return self.data.value

    @property
    def values(self) -> Sequence[RppStr]:
        return ()

    @property
    def span(self) -> RppSpan:
        return self.data.span


@dataclass(frozen=True)
class BinarySettings(Settings):
    settings: Sequence[RppStr]

    def __contains__(self, value: object) -> bool:
        return value in self.settings

    def __iter__(self) -> Iterator[Setting]:
        return map(lambda line: BinarySettingLine(line), iter(self.settings))

    def __len__(self) -> int:
        return len(self.settings)
