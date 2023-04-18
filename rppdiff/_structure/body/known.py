from dataclasses import dataclass
from itertools import chain
from typing import Collection, Iterator, Mapping, Sequence

from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.chunk import Body
from rppdiff._structure.body.generic import GenericSettings
from rppdiff._structure.body.settings import Setting, Settings
from rppdiff._structure.chunk import Chunk
from rppdiff.rppstr import RppStr


@dataclass(frozen=True)
class KnownSetting(Setting):
    rpp_name: RppStr
    rpp_values: Sequence[RppStr]
    known_name: str
    known_values: Sequence[str]

    span_: RppSpan

    @property
    def key(self) -> str:
        return self.known_name

    @property
    def values(self) -> Sequence[RppStr]:
        return self.rpp_values

    @property
    def span(self) -> RppSpan:
        return self.span_


@dataclass(frozen=True)
class KnownSettings(Settings):
    known: Mapping[str, KnownSetting]
    known_rpp_names: Collection[RppStr]
    unknown: GenericSettings

    def __contains__(self, value: object) -> bool:
        match value:
            case str():
                return value in self.known
            case _:
                return value in self.known_rpp_names or value in self.unknown

    def __iter__(self) -> Iterator[Setting]:
        return chain(self.known.values(), iter(self.unknown))

    def __len__(self) -> int:
        return len(self.known) + len(self.unknown)


@dataclass(frozen=True)
class KnownSettingsBody(Body):
    settings_: KnownSettings
    subchunks_: Sequence[Chunk]
    unique_subchunk_kinds_: Collection[str]

    @property
    def elements(self) -> Iterator[Setting | Chunk]:
        return chain(iter(self.settings_), iter(self.subchunks_))

    @property
    def settings(self) -> Settings:
        return self.settings_

    @property
    def subchunks(self) -> Iterator[Chunk]:
        return iter(self.subchunks_)

    @property
    def unique_subchunk_kinds(self) -> Collection[str]:
        return self.unique_subchunk_kinds_

    @property
    def subbodies(self) -> Iterator[Body]:
        return iter(())
