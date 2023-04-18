from dataclasses import dataclass
from typing import Collection, Iterator, Optional, Self

from rppdiff._diff.differ import Differ
from rppdiff._diff.result import DiffResult
from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.body.settings import Setting, Settings
from rppdiff._structure.chunk import Body, Chunk
from rppdiff.diff import Modify


@dataclass(frozen=True)
class IdentifiableBody(Body):
    id: str
    name: Optional[str]
    base: Body

    @property
    def elements(self) -> Iterator[Setting | Chunk | Body]:
        return self.base.elements

    @property
    def settings(self) -> Settings:
        return self.base.settings

    @property
    def subchunks(self) -> Iterator[Chunk]:
        return self.base.subchunks

    @property
    def unique_subchunk_kinds(self) -> Collection[str]:
        return self.base.unique_subchunk_kinds

    @property
    def subbodies(self) -> Iterator[Body]:
        return self.base.subbodies

    @property
    def chunk_id(self) -> Optional[str]:
        return self.id

    @property
    def chunk_name(self) -> Optional[str]:
        return self.name

    def diff(self: Self, other: Self, differ: Differ) -> DiffResult:
        if self.id != other.id:
            differ.append_deletion(str(self), at=self.span)
            differ.append_insertion(str(other), at=self.span)
            return DiffResult(True)

        result = DiffResult(True)
        match self.name, other.name:
            case str(), str():
                assert self.name is not None
                assert other.name is not None
                if self.name != other.name:
                    modification = Modify(
                        f'track name "{self.name}"', f'track name "{other.name}"')
                    differ.append_modification(modification, at=self.span)
            case str(), _:
                differ.append_deletion(
                    f'chunk name ({self.name})', at=self.span)
            case _, str():
                differ.append_insertion(
                    f'chunk name({other.name})', at=self.span)
            case _, _:
                result = DiffResult()

        return result | differ.diff(self.base, other.base)

    @property
    def span(self) -> RppSpan:
        return self.base.span

    @classmethod
    def is_same_as(cls, self: Self, other: Self) -> bool:
        '''Check whether self and other represent the "same" logical element.

        "Same" elements are not necessarily mathematically equal:
        they merely hint to diffing algorithms that the elements are approximately the same and their contents should be diffed.
        '''

        if self.id == other.id:
            return True
        else:
            return Body.is_same_as(self.base, other.base)

    def __str__(self) -> str:
        if self.chunk_name is not None:
            return f'"{self.chunk_name}" (id "{self.id}")'
        else:
            return f'"{self.id}"'
