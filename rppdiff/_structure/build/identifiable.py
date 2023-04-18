from typing import Iterable, Optional
from rppdiff._parser.elem import GenericBodyElem
from rppdiff._structure.body.identifiable import IdentifiableBody
from rppdiff._structure.build.body import BodyBuilder


class IdentifiableBodyBuilder(BodyBuilder):
    id_key: Optional[str]
    name_key: Optional[str]
    base_builder: BodyBuilder
    id: Optional[str]
    name: Optional[str]

    def __init__(self, base: BodyBuilder, id_key: Optional[str], name_key: Optional[str] = None, id: Optional[str] = None):
        self.base_builder = base
        self.name_key = name_key
        self.name = None

        if id is not None:
            self.id = id
            self.id_key = None
        else:
            self.id = None
            self.id_key = id_key

    def build(self, elems: Iterable[GenericBodyElem]) -> IdentifiableBody:
        body_elems: list[GenericBodyElem] = []
        for elem in elems:
            if self.id_key is not None:
                match elem:
                    case [key, *vals] if key.value == self.id_key:
                        self.id = vals[0].value
                        continue
                    case _:
                        pass

            if self.name_key is not None:
                match elem:
                    case [key, *vals] if key.value == self.name_key:
                        self.name = vals[0].value
                        continue
                    case _:
                        pass

            body_elems.append(elem)

        base = self.base_builder.build(body_elems)
        if self.id is None:
            raise RuntimeError('ID key was never found')

        return IdentifiableBody(id=self.id, name=self.name, base=base)
