from typing import Callable, Sequence
from rppdiff._diff.seq import DiffableSequence
from rppdiff._parser.rppspan import RppSpan
from rppdiff._structure.attributes.known import KnownAttribute, KnownAttributes

from rppdiff.rppstr import RppStr


AttValFn = Callable[[RppStr], str]


class KnownAttributesBuilder:
    attribute_info: Sequence[tuple[str, AttValFn]]

    def __init__(self, attribute_info: Sequence[tuple[str, AttValFn]]):
        self.attribute_info = attribute_info

    @classmethod
    def known_attribute(cls, a: tuple[RppStr, tuple[str, AttValFn]]) -> KnownAttribute:
        rpp_val, (known_name, known_val_fn) = a
        known_val = known_val_fn(rpp_val)
        return KnownAttribute(known_name=known_name, known_val=known_val, rpp_val=rpp_val)

    def build(self, attributes: Sequence[RppStr]) -> KnownAttributes:
        if len(attributes) > len(self.attribute_info):
            raise ValueError(
                'too many attributes passed: the builder does not have enough attribute information')

        attrs_ = zip(attributes, self.attribute_info)
        attrs = map(lambda a: KnownAttributesBuilder.known_attribute(a), attrs_)
        attrs_list = list(attrs)
        attrs_seq = DiffableSequence(
            attrs_list, RppSpan.all(map(lambda l: l.span, attrs_list)))
        return KnownAttributes(attrs_seq, attrs_seq.span)
