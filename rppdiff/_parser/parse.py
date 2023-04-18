from collections.abc import Sequence
from typing import Iterator, Optional, TextIO

from rppdiff._parser.elem import GenericBodyElem
from rppdiff._parser.scan import Token, TokenKind, tokenize
from rppdiff._structure.basic import BasicChunkInfo
from rppdiff._structure.build.new import new_chunk
from rppdiff._structure.chunk import Chunk
from rppdiff.rppstr import RppStr


ReaperProject = Chunk


class InvalidTokenError(RuntimeError):
    """Expected one token but got a different one."""

    expected_kind: TokenKind | Sequence[TokenKind]
    actual: Token

    def __init__(self, expected_kind: TokenKind | Sequence[TokenKind], actual: Token):
        self.expected_kind = expected_kind
        self.actual = actual
        super().__init__()

    def __str__(self) -> str:
        if isinstance(self.expected_kind, Sequence):
            if len(self.expected_kind) == 0:
                return f'Got invalid token {self.actual}'

            if len(self.expected_kind) == 1:
                expected = f'{self.expected_kind[0]}'
            else:
                expected = ""
                for k in self.expected_kind:
                    expected = expected + f'{k}, '
                expected = expected[:-2]

        else:
            expected = f'{self.expected_kind}'

        return f'Expected {expected} but got {self.actual}'


class NotAReaperProjectError(RuntimeError):
    def __str__(self) -> str:
        return "The input is not a full Reaper project: it is of a different chunk type."


class ExcessInputError(RuntimeError):
    project: ReaperProject

    def __init__(self, project: ReaperProject):
        self.project = project

    def __str__(self) -> str:
        return "A Reaper Project successfully parsed, but there was additional text after the REAPER_PROJECT chunk."


class UnexepctedEofError(RuntimeError):
    def __str__(self) -> str:
        return "Unexpected End-of-File."


class RppParser:
    """Parses a Reaper Project file contents into a nested chunk structure."""

    _scanner: Iterator[Token]
    _peeked: Optional[Token]

    def __init__(self, scanner: Iterator[Token]):
        """Make an RppParser directly from an iterator of Tokens.

        The tokenize generator from the rpp scanner module can be used here.

        It is better to use the from_str or from_rpp class methods instead of directly constructing an RppParser.
        """

        self._scanner = scanner
        self._peeked = None

    @classmethod
    def from_str(cls, str: str) -> 'RppParser':
        """Make an RppParser from the string contents of an RPP file."""

        scanner = tokenize(str)
        return cls(scanner)

    @classmethod
    def from_rpp(cls, rpp: TextIO) -> 'RppParser':
        """Make an RppParser from a file object."""

        return cls.from_str(rpp.read())

    def parse_project(self) -> ReaperProject:
        """Parse a full Reaper Project.

        NotAReaperProjectError is raised if the input isn't a full reaper project (e.g., the RPPXML output of ReaScript API call).
        """

        project = self.chunk()
        if project.kind != 'REAPER_PROJECT':
            raise NotAReaperProjectError()

        if not self._scanner_empty():
            raise ExcessInputError(project)

        return project

    def chunk(self) -> Chunk:
        """Parse a single chunk of any kind."""

        start_tok = self._consume(TokenKind.LBRACKET)
        chunk_kind, attributes = self._start_tag()
        body = self._chunk_body()
        end_tok = self._consume(TokenKind.RBRACKET)
        self._consume(TokenKind.NEWLINE)

        info = BasicChunkInfo.from_parts(chunk_kind, start_tok, end_tok)
        return new_chunk(info, attributes, body)

    def _start_tag(self) -> tuple[RppStr, list[RppStr]]:
        chunk_kind = self._word()
        attributes = self._fields()
        return chunk_kind, attributes

    def _fields(self) -> list[RppStr]:
        fields: list[RppStr] = []

        while self._peek() != TokenKind.NEWLINE:
            fields.append(self._field())

        self._consume(TokenKind.NEWLINE)
        return fields

    def _field(self) -> RppStr:
        next_tok = self._next()
        expected_kinds = [TokenKind.WORD, TokenKind.QUOTED_STRING]
        if next_tok.kind not in expected_kinds:
            raise InvalidTokenError(expected_kinds, next_tok)

        return RppStr.from_token(next_tok)

    def _chunk_body(self) -> list[GenericBodyElem]:
        body: list[GenericBodyElem] = []

        expected_kinds = [TokenKind.WORD, TokenKind.LBRACKET]
        while self._peek() in expected_kinds:
            match self._peek():
                case TokenKind.WORD:
                    body.append(self._property())
                case TokenKind.LBRACKET:
                    body.append(self.chunk())
                case otherwise:
                    raise ValueError(
                        f'Unreachable: {otherwise} not in expected kinds')

        return body

    def _property(self) -> list[RppStr]:
        # the list is guaranteed to have at least one element
        name = self._word()
        fields = self._fields()
        return [name] + fields

    def _word(self) -> RppStr:
        next_tok = self._next()
        if next_tok.kind != TokenKind.WORD:
            raise InvalidTokenError(TokenKind.WORD, next_tok)

        return RppStr.from_token(next_tok)

    def _consume(self, kind: TokenKind) -> Token:
        next_tok = self._next()
        if next_tok.kind != kind:
            raise InvalidTokenError(kind, next_tok)

        return next_tok

    def _peek(self) -> TokenKind | None:
        if self._peeked is None:
            self._peeked = next(self._scanner, None)

        if self._peeked is None:
            return None

        return self._peeked.kind

    def _next(self) -> Token:
        if self._peeked is not None:
            next_tok = self._peeked
            self._peeked = None
        else:
            next_tok = self._next_from_scanner()

        return next_tok

    def _next_from_scanner(self) -> Token:
        try:
            return next(self._scanner)
        except StopIteration as e:
            raise UnexepctedEofError(
                'Unexpected End-of-File encountered.') from e

    def _scanner_empty(self) -> bool:
        peeked = self._peek()
        return peeked is None


def parse_str(str: str) -> ReaperProject:
    """Attempt to parse a reaper project from the string contents of the file."""
    parser = RppParser.from_str(str)
    return parser.parse_project()


def parse_rpp(file: TextIO) -> ReaperProject:
    """Attempt to parse a reaper project from its file."""
    parser = RppParser.from_rpp(file)
    return parser.parse_project()
