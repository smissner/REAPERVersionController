from pathlib import Path
from typing import Optional, Sequence, TextIO

from rppdiff._diff.differ import Differ
from rppdiff._parser.parse import ReaperProject, RppParser
from rppdiff.diff import Diff


Rpp = TextIO | Path | str


def _parser_for(rpp: Rpp) -> RppParser:
    match rpp:
        case TextIO():
            return RppParser.from_rpp(rpp)

        case Path():
            with open(rpp.resolve()) as rpp_file:
                return RppParser.from_rpp(rpp_file)

        case str():
            return RppParser.from_str(rpp)


def _project_from(rpp: Rpp) -> ReaperProject:
    parser = _parser_for(rpp)
    return parser.parse_project()


def _source_for(rpp: Rpp) -> Optional[str]:
    match rpp:
        case Path():
            return str(rpp)

        case _:
            return None


def _differ_for(old: Rpp, new: Rpp) -> Differ:
    old_source = _source_for(old)
    new_source = _source_for(new)

    return Differ(old_source, new_source)


def diff_rpps(old: Rpp, new: Rpp) -> Sequence[Diff]:
    '''Find the differences between two Reaper Project files.

    The old and new RPP files may each be input as one of:

    * a `Path` to the file (most recommended)
    * the file object itself, as returned from `open()`
    * the string contents of the file

    It is recommended to give `Path`s to the files if possible, as the diff messages will be best and the file reading will be efficient.
    `Path`s will be automatically resolved via `resolve()`.

    This function returns a list of `Diff` objects.
    Each `Diff` can be printed or converted to a string to obtain a diff message.
    Diff messages usually take up multiple lines.'''

    old_project = _project_from(old)
    new_project = _project_from(new)
    differ = _differ_for(old, new)
    differ.diff(old_project, new_project)
    return differ.diffs
