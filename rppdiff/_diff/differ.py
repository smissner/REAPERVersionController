from contextlib import contextmanager
from enum import Enum
from typing import Generator, Optional, Protocol, Self, Sequence, TypeVar

from rppdiff._diff.result import DiffResult
from rppdiff._parser.rppspan import RppSpan
from rppdiff.diff import Diff, DiffCtx, Edit, EditOperand, EditOperation, Modify


class Diffable(Protocol):
    def diff(self: Self, other: Self, differ: 'Differ') -> DiffResult:
        ...

    @property
    def span(self) -> RppSpan:
        ...

    def ctx(self) -> Optional[str]:
        '''If this diffable item bears some extra context, it can be returned here.

        This is useful for situations where a parent Diffable doesn't know what its child's context should be.
        '''

        return None

    @classmethod
    def is_same_as(cls, self: Self, other: Self) -> bool:
        '''Check whether self and other represent the "same" logical element.

        "Same" elements are not necessarily mathematically equal:
        they merely hint to diffing algorithms that the elements are approximately the same and their contents should be diffed.
        '''

        return self == other


class _EditSource(Enum):
    OLD = "old"
    NEW = "new"


_D = TypeVar("_D", bound=Diffable)


class Differ:
    _ctx: DiffCtx
    _old_source: str
    _new_source: str
    _diffs: list[Diff]

    def __init__(self, old_source: Optional[str] = None, new_source: Optional[str] = None):
        self._ctx = []
        self._old_source = old_source or "old"
        self._new_source = new_source or "new"
        self._diffs = []

    def diff(self, old: _D, new: _D) -> DiffResult:
        ctx = old.ctx()
        with self.context(ctx):
            return old.diff(new, self)

    def diff_with_ctx(self, ctx: str, old: _D, new: _D) -> DiffResult:
        with self.context(ctx):
            return self.diff(old, new)

    def diff_all(self, *items: tuple[_D, _D]) -> DiffResult:
        result = DiffResult()
        for old, new in items:
            result = result or self.diff(old, new)

        return result

    @property
    def diffs(self) -> Sequence[Diff]:
        return self._diffs

    @contextmanager
    def context(self, context: Optional[str]) -> Generator[None, None, None]:
        if context is not None:
            self._ctx.append(context)
            yield
            self._ctx.pop()
        else:
            yield

    def append_deletion(self, operand: str, at: RppSpan) -> None:
        self._append_diff(EditOperation.DELETE, operand, at, _EditSource.OLD)

    def append_insertion(self, operand: str, at: RppSpan) -> None:
        self._append_diff(EditOperation.INSERT, operand, at, _EditSource.NEW)

    def append_modification(self, operand: Modify, at: RppSpan) -> None:
        self._append_diff(EditOperation.MODIFY, operand, at, _EditSource.OLD)

    def _append_diff(self, operation: EditOperation, operand: EditOperand, at: RppSpan, source: _EditSource) -> None:
        match source:
            case _EditSource.OLD:
                edit_src = self._old_source
            case _EditSource.NEW:
                edit_src = self._new_source

        edit = Edit(operation, operand, at, edit_src)
        diff = Diff(self._ctx_copied(), edit)
        self._diffs.append(diff)

    def _append_ctx(self, context: str) -> None:
        self._ctx.append(context)

    def _pop_ctx(self) -> None:
        self._ctx.pop()

    def _ctx_copied(self) -> DiffCtx:
        return self._ctx.copy()
