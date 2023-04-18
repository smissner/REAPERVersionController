from typing import Iterable, Sequence

from rppdiff._diff.seq import DiffableSequence
from rppdiff._parser.elem import GenericBodyElem
from rppdiff._parser.rppspan import RppLocation, RppSpan
from rppdiff._structure.attributes.generic import GenericAttributes
from rppdiff._structure.body.generic import GenericBody, GenericSetting, GenericSettings
from rppdiff._structure.body.settings import Setting
from rppdiff._structure.build.body import BodyBuilder
from rppdiff._structure.chunk import Chunk
from rppdiff.rppstr import RppStr


class GenericAttributesBuilder:
    start: RppLocation

    def __init__(self, start: RppLocation):
        self.start = start

    def build(self, attributes: Sequence[RppStr]) -> GenericAttributes:
        seq = DiffableSequence.new(attributes, loc=self.start)
        return GenericAttributes(seq)


class GenericBodyBuilder(BodyBuilder):
    start: RppLocation

    def __init__(self, start: RppLocation):
        self.start = start

    def build(self, elems: Iterable[GenericBodyElem]) -> GenericBody:
        def elems_same(a: Setting | Chunk, b: Setting | Chunk) -> bool:
            match a, b:
                case Setting(), Setting():
                    return Setting.is_same_as(a, b)  # type: ignore
                case Chunk(), Chunk():
                    return Chunk.is_same_as(a, b)  # type: ignore
                case _, _:
                    return False

        subchunks: list[Chunk] = []
        settings: list[Sequence[RppStr]] = []
        elems_: list[Setting | Chunk] = []
        for elem in elems:
            match elem:
                case Chunk():
                    subchunks.append(elem)
                    elems_.append(elem)
                case _:
                    settings.append(elem)
                    span = RppSpan.all(map(lambda e: e.span, elem))
                    setting = GenericSetting.from_kv(
                        (elem[0].value, (span, elem[1:])))
                    elems_.append(setting)

        generic_settings = GenericSettings.new(settings)
        unique_subchunk_kinds = set(map(lambda c: c.kind, subchunks))
        elements = DiffableSequence(
            elems_, RppSpan.empty(self.start), 'chunk', elems_same)

        return GenericBody(elements, generic_settings, subchunks, unique_subchunk_kinds)
