from dataclasses import dataclass
from typing import Collection, Iterator, Optional, Protocol, Self

from rppdiff._diff.differ import Diffable, Differ
from rppdiff._diff.result import DiffResult
from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.attributes.attributes import Attributes
from rppdiff._structure.basic import BasicChunkInfo
from rppdiff._structure.body.settings import Setting, Settings


class Body(Diffable, Protocol):
    '''The base type for chunk bodies.

    This is a base protocol (interface) that cannot be instantiated on its own.
    Bodies are `Diffable`.

    A body consists of a sequence of `elements`, which can be either settings or sub-chunks.
    Some bodies also consist of a sequence of sub-bodies.
    '''

    @property
    def elements(self) -> Iterator['Setting | Chunk | Body']:
        '''An iterator over the elements of the body.

        Each sub-body is considered one element for this property.
        '''

        ...

    @property
    def settings(self) -> Settings:
        ...

    @property
    def subchunks(self) -> Iterator['Chunk']:
        ...

    @property
    def unique_subchunk_kinds(self) -> Collection[str]:
        ...

    @property
    def subbodies(self) -> Iterator['Body']:
        ...

    @property
    def chunk_id(self) -> Optional[str]:
        return None

    @property
    def chunk_name(self) -> Optional[str]:
        return None


@dataclass(frozen=True)
class Chunk(Diffable):
    kind: str
    attributes: Attributes
    body: Body
    span_: RppSpan

    id: Optional[str]
    name: Optional[str]

    @classmethod
    def new(cls, info: BasicChunkInfo, attributes: Attributes, body: Body, id: Optional[str] = None, name: Optional[str] = None) -> 'Chunk':
        return Chunk(info.kind.value, attributes, body, info.span, id, name)

    def diff(self: Self, other: Self, differ: Differ) -> DiffResult:
        ids_different = self.id is not None and other.id is not None and self.id != other.id

        if ids_different or self.kind != other.kind:
            differ.append_deletion(f'chunk {self.kind}', at=self.span)
            differ.append_insertion(f'chunk {other.kind}', at=other.span)
            return DiffResult(True)

        return differ.diff(self.attributes, other.attributes) | differ.diff(self.body, other.body)

    @property
    def span(self) -> RppSpan:
        return self.span_

    @classmethod
    def is_same_as(cls, self: Self, other: Self) -> bool:
        return Attributes.is_same_as(self.attributes, other.attributes) or Body.is_same_as(self.body, other.body)

    def __str__(self) -> str:
        out = ""
        if self.name is not None:
            out += f'"{self.name}"'
        else:
            out += self.kind

        if self.id is not None:
            out += f' (id {self.id})'

        return out
