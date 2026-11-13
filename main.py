# ai-happy-01 v2 entry (Python 3.13, standard library only).
#
# The image is drawn at build time by generate.py (Pillow) and shipped in
# this repository as entry.png. The grading runtime has no Pillow and no
# network, so this program only copies the finished image to the output
# directory: /output/entry.png
import os
import shutil

os.makedirs("/output", exist_ok=True)
shutil.copyfile(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"),
    "/output/entry.png",
)
