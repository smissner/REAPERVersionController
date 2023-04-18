from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class DiffResult:
    difference_present: bool = False

    def __or__(self, other: Self) -> 'DiffResult':
        return DiffResult(self.difference_present or other.difference_present)

    def __and__(self, other: Self) -> 'DiffResult':
        return DiffResult(self.difference_present and other.difference_present)
