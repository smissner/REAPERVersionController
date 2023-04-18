from dataclasses import dataclass
from enum import Enum, auto
from typing import NamedTuple

from rppdiff._parser.rppspan import RppSpan


class EditOperation(Enum):
    INSERT = auto()
    DELETE = auto()
    MODIFY = auto()


class Modify(NamedTuple):
    change_from: str
    change_to: str

    def __str__(self) -> str:
        return f'from `{self.change_from}` to `{self.change_to}`'


EditOperand = Modify | str


@dataclass(frozen=True)
class Edit:
    operation: EditOperation
    operand: EditOperand
    span: RppSpan
    source: str

    def __str__(self) -> str:
        match self.operation:
            case EditOperation.INSERT:
                return f'insert `{self.operand}` ({self.source}, {self.span})'
            case EditOperation.DELETE:
                return f'delete `{self.operand}` ({self.source}, {self.span})'
            case EditOperation.MODIFY:
                assert isinstance(self.operand, Modify)
                return f'change {self.operand} ({self.source}, {self.span})'


DiffCtx = list[str]


@dataclass(frozen=True)
class Diff:
    ctx: DiffCtx
    edit: Edit

    def __str__(self) -> str:
        out = str(self.edit)
        for context in reversed(self.ctx):
            out += f'\n  | {context}'

        return out
