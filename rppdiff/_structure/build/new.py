from typing import Sequence, TypeVar

from rppdiff._parser.elem import GenericBodyElem
from rppdiff._structure.basic import BasicChunkInfo
from rppdiff._structure.build.body import BodyBuilder
from rppdiff._structure.build.generic import GenericAttributesBuilder, GenericBodyBuilder
from rppdiff._structure.build.identifiable import IdentifiableBodyBuilder
from rppdiff._structure.build.known_attributes import KnownAttributesBuilder
from rppdiff._structure.chunk import Chunk
from rppdiff.rppstr import RppStr

_T = TypeVar('_T')


def _rppstr_val(x: RppStr) -> str:
    return x.value


_REAPER_PROJECT_ATTRIBUTE_INFO = [
    ('file version', _rppstr_val),
    ('REAPER version', _rppstr_val),
    ('last modified time', _rppstr_val)
]


def new_chunk(info: BasicChunkInfo, attributes: Sequence[RppStr], body: Sequence[GenericBodyElem]) -> Chunk:
    base_body_builder = GenericBodyBuilder(info.span.start)
    body_builder: BodyBuilder

    match info.kind.value:
        case "REAPER_PROJECT":
            attributes_builder = KnownAttributesBuilder(
                _REAPER_PROJECT_ATTRIBUTE_INFO)
            body_builder = base_body_builder
        case "TRACK":
            attributes_builder = GenericAttributesBuilder(info.span.start)
            body_builder = IdentifiableBodyBuilder(
                base=base_body_builder, id_key="TRACKID", name_key="NAME")
        case "ITEM":
            attributes_builder = GenericAttributesBuilder(info.span.start)
            body_builder = IdentifiableBodyBuilder(
                base=base_body_builder, id_key="IGUID")
        case _:
            attributes_builder = GenericAttributesBuilder(info.span.start)
            body_builder = base_body_builder

    body_ = body_builder.build(body)
    attributes_ = attributes_builder.build(attributes)
    return Chunk.new(info, attributes_, body_)
