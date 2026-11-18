#!/usr/bin/env python3
"""news-image-20261117 entry (Python 3.13, standard library only).

The entry image is entry.png beside this file: a front page drawn
programmatically for Tuesday 17 November 2026 (see gen.py, which drew
it with PIL - bridge, tanker, flags, phone and rocket scenes are all
original drawn artwork, no copied photos). The program copies it
byte-for-byte to /output/entry.png, so both grader runs write the
same bytes. No network.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
