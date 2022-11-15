import os
import re
import subprocess
import sys

REAPER_PATH_MAC = '/Applications/REAPER.app/Contents/MacOS/REAPER'


def set_render_outfile(rpp_path: str, out_audio_name: str, copy=True) -> str:
    '''
    Set the name of the audio file that REAPER will render to.
    This will modify the file at `rpp_path` if `copy` is false.

    If `copy` is true (default), then the resulting RPP file is saved to `name.rpp` in the same directory.

    Returns the path of the RPP file with the audio render outfile set appropriately.
    '''

    in_path = rpp_path
    head, tail = os.path.split(rpp_path)
    in_rpp_name, ext = os.path.splitext(tail)

    if copy:
        out_rpp_name = out_audio_name
    else:
        out_rpp_name = in_rpp_name

    out_path = os.path.join(head, out_rpp_name + ext)

    with open(in_path, 'r') as rpp:
        contents = rpp.read()

    contents = re.sub(r'RENDER_PATTERN\s+(.+)',
                      f'RENDER_PATTERN {out_audio_name}',
                      contents)

    with open(out_path, 'w') as rpp:
        print(contents, file=rpp)

    return out_path


def render(rpp_path: str):
    '''
    Render the reaper project file at `rpp_path` using REAPER.
    The rpp file *must* contain render information or else the render will silently fail.
    '''

    match sys.platform:
        case 'darwin':
            reaper_path = REAPER_PATH_MAC
        case _:
            raise NotImplementedError('TODO: add windows support')

    args = [reaper_path, '-renderproject', rpp_path]
    subprocess.run(args, capture_output=True, check=True)


if __name__ == '__main__':
    rpp = os.path.expanduser('~/Downloads/testsc/testsc.rpp')

    out_rpp = set_render_outfile(rpp, 'test')
    render(out_rpp)
