import os
import shutil


def clear_files() -> None:
    files_to_clear = [
        "data/output/debug",
        "data/output/recombined",
        "data/output/split",
    ]
    for folder in files_to_clear:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)
