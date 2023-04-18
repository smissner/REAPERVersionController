from dataclasses import dataclass
from typing import Callable, Generic, Optional, overload, Self, Sequence, TypeVar

from rppdiff._diff.differ import Diffable, Differ
from rppdiff._diff.myers import EditOp, MyersDiff
from rppdiff._diff.result import DiffResult
from rppdiff._parser.rppspan import RppLocation, RppSpan

_D = TypeVar('_D', bound=Diffable)
_Eq = Callable[[_D, _D], bool]


@dataclass(frozen=True)
class DiffableSequence(Diffable, Sequence[_D], Generic[_D]):
    _seq: Sequence[_D]
    _span: RppSpan
    _index_str: str = 'index'
    _elems_same: _Eq[_D] = Diffable.is_same_as

    @overload
    @classmethod
    def new(cls, loc_or_seq: RppLocation, elems_same: Optional[_Eq[_D]] = None, index_str: Optional[str] = None, loc: Optional[RppLocation] = None) -> 'DiffableSequence[_D]':
        '''Create an empty sequence at a location.'''
        ...

    @overload
    @classmethod
    def new(cls, loc_or_seq: Sequence[_D], elems_same: Optional[_Eq[_D]] = None, index_str: Optional[str] = None, loc: Optional[RppLocation] = None) -> 'DiffableSequence[_D]':
        '''Create a DiffableSequence from a sequence.

        It is an error to pass an empty sequence unless start is set (to a non-None value).'''
        ...

    @classmethod
    def new(cls, loc_or_seq: RppLocation | Sequence[_D], elems_same: Optional[_Eq[_D]] = None, index_str: Optional[str] = None, loc: Optional[RppLocation] = None) -> 'DiffableSequence[_D]':
        match loc_or_seq:
            case RppLocation():
                return cls._new_empty(loc_or_seq)
            case _:
                return cls._new_potentially_empty(loc_or_seq, elems_same, index_str, loc)

    @classmethod
    def _new_empty(cls, loc: RppLocation) -> 'DiffableSequence[_D]':
        seq = ()
        span = RppSpan.empty(loc)
        return DiffableSequence(seq, span)

    @classmethod
    def _new_nonempty(cls, seq: Sequence[_D], elems_same: Optional[_Eq[_D]], index_str: Optional[str]) -> 'DiffableSequence[_D]':
        spans = map(lambda d: d.span, seq)
        span = RppSpan.all(spans)

        kwargs = {}
        if index_str is not None:
            kwargs['index_str'] = index_str
        if elems_same is not None:
            kwargs['elems_same'] = elems_same  # type: ignore

        return DiffableSequence(seq, span, **kwargs)  # type: ignore

    @classmethod
    def _new_potentially_empty(cls, seq: Sequence[_D], elems_same: Optional[_Eq[_D]], index_str: Optional[str], loc: Optional[RppLocation]) -> 'DiffableSequence[_D]':
        if len(seq) == 0:
            if loc is None:
                raise ValueError('start must be provided if sequence is empty')

            return cls._new_empty(loc)

        return cls._new_nonempty(seq, elems_same, index_str)

    @overload
    def __getitem__(self, index: int) -> _D:
        ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[_D]:
        ...

    def __getitem__(self, index: int | slice) -> _D | Sequence[_D]:
        return self._seq[index]

    def __len__(self) -> int:
        return len(self._seq)

    def diff(self: Self, other: Self, differ: Differ) -> DiffResult:
        myers = MyersDiff(self, other)

        consecutive_deletes = 0
        last_op = EditOp.UNMOVED_POSSIBLY_MODIFIED

        diff_result = DiffResult()

        for op, start, _ in myers.diff(self._elems_same):
            old_idx, new_idx = start
            # make sure old_idx is positive for printing
            if old_idx < 0:
                old_idx = len(self) + old_idx

            match op:
                case EditOp.DELETE:
                    deleted = self[old_idx]
                    with differ.context(f'at {self._index_str} {old_idx}'):
                        differ.append_deletion(str(deleted), at=deleted.span)

                    consecutive_deletes += 1
                    diff_result = DiffResult(True)

                case EditOp.INSERT:
                    if last_op in [EditOp.DELETE, EditOp.INSERT] and consecutive_deletes > 0:
                        ctx = differ.context(
                            f'at {self._index_str} {old_idx - consecutive_deletes}')
                        consecutive_deletes -= 1
                    else:
                        ctx = differ.context(f'at {self._index_str} {old_idx}')

                    inserted = other[new_idx]
                    with ctx:
                        differ.append_insertion(
                            str(inserted), at=inserted.span)

                    diff_result = DiffResult(True)

                case EditOp.UNMOVED_POSSIBLY_MODIFIED:
                    res = differ.diff_with_ctx(f'at {self._index_str} {old_idx}',
                                               self[old_idx], other[new_idx])

                    diff_result = diff_result | res
                    consecutive_deletes = 0

            last_op = op

        return diff_result

    @property
    def span(self) -> RppSpan:
        return self._span

    pass
