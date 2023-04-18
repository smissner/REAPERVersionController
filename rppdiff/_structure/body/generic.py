from dataclasses import dataclass
from typing import Collection, Iterator, Mapping, Self, Sequence

from rppdiff._diff.differ import Differ
from rppdiff._diff.result import DiffResult
from rppdiff._diff.seq import DiffableSequence
from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.chunk import Body
from rppdiff._structure.body.settings import Setting, Settings
from rppdiff._structure.chunk import Chunk
from rppdiff.rppstr import RppStr


@dataclass(frozen=True)
class GenericSetting(Setting):
    key_: str
    values_: DiffableSequence[RppStr]
    span_: RppSpan

    @classmethod
    def from_kv(cls, key_values: tuple[str, tuple[RppSpan, Sequence[RppStr]]]) -> 'GenericSetting':
        k, (span, vals) = key_values
        values = DiffableSequence(vals, span)
        return GenericSetting(k, values, span)

    @property
    def key(self) -> str:
        return self.key_

    @property
    def values(self) -> Sequence[RppStr]:
        return self.values_

    def diff(self: Self, other: Self, differ: Differ) -> DiffResult:
        if self.key != other.key:
            differ.append_deletion(str(self), at=self.span)
            differ.append_insertion(str(other), at=other.span)
            return DiffResult(True)

        return differ.diff(self.values_, other.values_)

    @property
    def span(self) -> RppSpan:
        return self.span_


@dataclass(frozen=True)
class GenericSettings(Settings):
    settings: Mapping[str, tuple[RppSpan, Sequence[RppStr]]]

    @classmethod
    def new(cls, settings: Sequence[Sequence[RppStr]]) -> 'GenericSettings':
        settings_ = {}

        for setting in settings:
            span = RppSpan.all(map(lambda s: s.span, setting))
            k = setting[0].value
            v = setting[1:]
            settings_[k] = span, v

        return GenericSettings(settings_)

    def __contains__(self, value: object) -> bool:
        return value in self.settings

    def __iter__(self) -> Iterator[Setting]:
        return map(lambda s: GenericSetting.from_kv(s), self.settings.items())

    def __len__(self) -> int:
        return len(self.settings)


@dataclass(frozen=True)
class GenericBody(Body):
    elems: DiffableSequence[Setting | Chunk]
    settings_: GenericSettings
    subchunks_: Sequence[Chunk]
    unique_subchunk_kinds_: Collection[str]

    @property
    def elements(self) -> Iterator[Setting | Chunk]:
        return iter(self.elems)

    @property
    def settings(self) -> Settings:
        return self.settings

    @property
    def subchunks(self) -> Iterator[Chunk]:
        return iter(self.subchunks_)

    @property
    def unique_subchunk_kinds(self) -> Collection[str]:
        return self.unique_subchunk_kinds_

    @property
    def subbodies(self) -> Iterator[Body]:
        return iter(())

    def diff(self: Self, other: Self, differ: Differ) -> DiffResult:
        return differ.diff(self.elems, other.elems)

    @property
    def span(self) -> RppSpan:
        return self.elems.span
