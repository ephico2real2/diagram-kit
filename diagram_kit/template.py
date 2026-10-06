"""diagram-template <path/to/source.html>: start a diagram's page from the template this installed kit ships.

The template is package data, so one pin carries the renderer, its checks and the template they were tested against.
An existing page is never overwritten: re-running the command on a diagram must not wipe it.
"""

from __future__ import annotations

import pathlib
import sys
from importlib.resources import files


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.splitlines()[0], file=sys.stderr)
        return 2
    target = pathlib.Path(sys.argv[1])
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as stream:
            stream.write(files("diagram_kit").joinpath("template.html").read_bytes())
    except FileExistsError:
        print(f"refusing to overwrite {target}", file=sys.stderr)
        return 1
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
