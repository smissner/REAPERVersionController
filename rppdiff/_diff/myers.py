# heavily based on:
# * Myers 1986 (An O(ND) algorithm and its variations)
# * https://blog.jcoglan.com/2017/02/17/the-myers-diff-algorithm-part-1/

from enum import Enum, auto
import operator
from typing import Any, Callable, Generator, Generic, NamedTuple, Sequence, TypeVar

_T = TypeVar('_T')
_Eq = Callable[[_T, _T], bool]
_Accumulate = Callable[[list[int]], None]


def _do_nothing(x: Any) -> None: return None


class EditOp(Enum):
    UNMOVED_POSSIBLY_MODIFIED = auto()
    INSERT = auto()
    DELETE = auto()


class EditCoord(NamedTuple):
    old_idx: int
    new_idx: int


class EditMove(NamedTuple):
    op: EditOp
    start: EditCoord
    end: EditCoord  # not technically needed


class MyersDiff(Generic[_T]):
    old: Sequence[_T]
    new: Sequence[_T]

    def __init__(self, old: Sequence[_T], new: Sequence[_T]):
        self.old = old
        self.new = new

    def _shortest_edit_path_acc(self, elems_equal: _Eq[_T] = operator.eq, accumulate: _Accumulate = _do_nothing) -> int:
        '''Generic shortest edit path.

        To track the exact path, O((n+m)*d) space is needed.
        If only the length of the path is needed, the space penalty is not needed, so no accumulation is necessary.

        '''

        # variables from Myers1986
        # A :   old_len
        # B :   new_len
        # MAX : max_edit_len
        # D :   edit_len
        # X :   old_idx
        # Y :   new_idx
        # K :   diagonal
        # V :   max_old_on_diags

        old_len = len(self.old)
        new_len = len(self.new)
        max_edit_len = old_len + new_len

        if max_edit_len == 0:
            return 0

        # stores the highest old index explored along each diagonal
        # diagonal -1 is stored at max_old_on_diags[-1], etc.
        max_old_on_diags = [0] * (2 * max_edit_len + 1)

        # explore edits breath-first until the first path reaches the end of old and new
        for edit_len in range(0, max_edit_len + 1):
            accumulate(max_old_on_diags.copy())

            # choose the point to connect to each new explored point, prioritizing deletes from old first
            for diagonal in range(-edit_len, edit_len + 1, 2):
                if diagonal == -edit_len or (diagonal != edit_len and max_old_on_diags[diagonal-1] < max_old_on_diags[diagonal+1]):
                    # move downward, so new old idx is same as previous
                    old_idx = max_old_on_diags[diagonal + 1]
                else:
                    # move rightward
                    old_idx = max_old_on_diags[diagonal - 1] + 1

                new_idx = old_idx - diagonal

                # take as many diagonal steps as possible from this point, for free
                while old_idx < old_len and new_idx < new_len and elems_equal(self.old[old_idx], self.new[new_idx]):
                    old_idx += 1
                    new_idx += 1

                max_old_on_diags[diagonal] = old_idx

                # we've reached the end
                if old_idx >= old_len and new_idx >= new_len:
                    return edit_len

        raise RuntimeError('unreachable')

    def shortest_edit_len(self, elems_equal: _Eq[_T] = operator.eq) -> int:
        return self._shortest_edit_path_acc(elems_equal)

    def _shortest_edit_path_trace(self, elems_equal: _Eq[_T] = operator.eq) -> list[list[int]]:
        trace: list[list[int]] = []

        def acc(step: list[int]) -> None:
            trace.append(step)

        self._shortest_edit_path_acc(elems_equal, acc)

        return trace

    def backtrack_trace(self, trace: list[list[int]]) -> Generator[EditMove, None, None]:
        x = len(self.old)
        y = len(self.new)

        if len(trace) == 1:
            for i in reversed(range(x)):
                start = EditCoord(i - 1, i - 1)
                end = EditCoord(i, i)
                yield EditMove(EditOp.UNMOVED_POSSIBLY_MODIFIED, start, end)

            return

        for v, d in zip(reversed(trace), range(len(trace)-1, 0, -1)):
            k = x - y

            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                prev_k = k + 1
            else:
                prev_k = k - 1

            prev_x = v[prev_k]
            prev_y = prev_x - prev_k

            while x > prev_x and y > prev_y:
                start = EditCoord(x - 1, y - 1)
                end = EditCoord(x, y)
                yield EditMove(EditOp.UNMOVED_POSSIBLY_MODIFIED, start, end)

                x = x - 1
                y = y - 1

            if d > 0:
                start = EditCoord(prev_x, prev_y)
                end = EditCoord(x, y)
                if x > prev_x and y == prev_y:
                    op = EditOp.DELETE
                elif x == prev_x and y > prev_y:
                    op = EditOp.INSERT
                else:
                    op = EditOp.UNMOVED_POSSIBLY_MODIFIED

                yield EditMove(op, start, end)

            x = prev_x
            y = prev_y

    def diff(self, elems_equal: _Eq[_T] = operator.eq) -> list[EditMove]:
        trace = self._shortest_edit_path_trace(elems_equal)

        diff: list[EditMove] = []
        for move in self.backtrack_trace(trace):
            diff.insert(0, move)

        return diff
