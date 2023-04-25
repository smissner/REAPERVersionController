from dataclasses import dataclass
from itertools import chain
from typing import Collection, Iterator, Sequence

from rppdiff._structure.chunk import Body
from rppdiff._structure.body.settings import Setting, Settings
from rppdiff._structure.chunk import Chunk


@dataclass(frozen=True)
class BodyWithSubbodies(Body):
    main: Body
    subbodies_: Sequence[Body]

    @property
    def elements(self) -> Iterator[Setting | Chunk | Body]:
        return chain(self.main.elements, chain(self.subbodies_))

    @property
    def settings(self) -> Settings:
        return self.main.settings

    @property
    def subchunks(self) -> Iterator[Chunk]:
        return self.main.subchunks

    @property
    def unique_subchunk_kinds(self) -> Collection[str]:
        return self.main.unique_subchunk_kinds

    @property
    def subbodies(self) -> Iterator[Body]:
        return iter(self.subbodies_)
