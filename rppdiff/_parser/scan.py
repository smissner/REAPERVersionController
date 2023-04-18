from enum import Enum
from typing import Generator, NamedTuple
import re

from .rppspan import RppLocation, RppSpan

_token_regex: re.Pattern[str]


def _init_regex() -> None:
    global _token_regex

    tokens = [
        ('LBRACKET', '<'),
        ('RBRACKET', '>'),
        ('NEWLINE', '\n'),
        ('QUOTED_STRING', r'"[^\n]*"'),
        ('WORD', r'[^"<> \t\n]+'),
        ('WHITESPACE', '[ \t]+'),
        ('ERROR', "."),
    ]

    regex = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
    _token_regex = re.compile(regex)


_init_regex()


class TokenKind(Enum):
    LBRACKET = 'LBRACKET'
    RBRACKET = 'RBRACKET'
    NEWLINE = 'NEWLINE'
    QUOTED_STRING = 'QUOTED_STRING'
    WORD = 'WORD'


class Token(NamedTuple):
    kind: TokenKind
    value: str
    span: RppSpan


class TokenError(RuntimeError):
    """A bad token has been scanned."""


def tokenize(rpp: str) -> Generator[Token, None, None]:
    line = 0
    line_start_idx = 0

    for match in _token_regex.finditer(rpp):
        kind_str = match.lastgroup
        value = match.group()

        match kind_str:
            case 'LBRACKET':
                kind = TokenKind.LBRACKET

            case 'RBRACKET':
                kind = TokenKind.RBRACKET

            case 'NEWLINE':
                kind = TokenKind.NEWLINE
                line += 1
                line_start_idx = match.start() + 1

            case 'QUOTED_STRING':
                kind = TokenKind.QUOTED_STRING
                value = value[1:-1]  # strip quotes from string

            case 'WORD':
                kind = TokenKind.WORD

            case 'WHITESPACE':
                continue

            case  _:
                raise TokenError('`{value!r}` unexpected')

        start_col = match.start() - line_start_idx
        end_col = match.end() - line_start_idx
        start = RppLocation(line, start_col)
        end = RppLocation(line, end_col)

        yield Token(kind=kind, value=value, span=RppSpan(start, end))
