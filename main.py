"""news-image-20261117 entry (Python 3.13, standard library only).

The image is the entry.png beside this file: a dense newspaper front
page summing up Tuesday 17 November 2026 (43 stories, 6 continents).
The program copies it to the output directory as entry.png.
Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
/output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

OUT.mkdir(parents=True, exist_ok=True)
source = HERE / "entry.png"
target = OUT / "entry.png"
shutil.copyfile(source, target)
# Fail loudly rather than hand the grader a truncated copy.
if target.stat().st_size != source.stat().st_size:
    raise SystemExit("entry.png copy incomplete: sizes differ")
