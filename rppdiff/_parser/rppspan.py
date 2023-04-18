from typing import Iterator, NamedTuple, Self


class RppLocation(NamedTuple):
    line: int
    col: int


class RppSpan(NamedTuple):
    start: RppLocation
    '''The first character of the span.'''

    end: RppLocation
    '''One character past the end of the span.'''

    @classmethod
    def empty(cls, location: RppLocation) -> 'RppSpan':
        return RppSpan(location, location)

    @classmethod
    def all(cls, spans: Iterator[Self]) -> 'RppSpan':
        '''Get the span covering an entire collection of spans.

        The parameter spans must contain at least one span.'''

        try:
            first = next(iter(spans))
        except:
            raise ValueError('must provide at least one span')

        start = first.start
        end = first.end

        for span in spans:
            if span.start < start:
                start = span.start
            if span.end > end:
                end = span.end

        return RppSpan(start, end)

    def __str__(self) -> str:
        return f'line {self.start.line + 1}, col {self.start.col + 1}'
