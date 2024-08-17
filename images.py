import time
from pathlib import Path
from typing import List


class Image:

    def __init__(self, p: Path):
        self.path = str(p)
        self.name: str = p.stem
        self.disk_usage: int = sum([f.stat().st_size for f in p.rglob("*") if f.is_file()])
        self.occurrences: List[Path] = []

    @property
    def is_unused(self) -> bool:
        return not self.occurrences


def include_dir_in_search(entry: str) -> bool:
    return entry not in ["Pods", "Images.xcassets"] and not entry.startswith(".") and not entry.endswith(".framework")

start_time = time.time()
project_root = Path.home().joinpath("work/ios")
images = [Image(p=entry) for entry in project_root.rglob("*.imageset") if "Pods" not in entry.parts]

# Search for occurrence of each image in all files
for root, dirs, files in project_root.walk():
    dirs = [d for d in dirs if include_dir_in_search(d)]
    for file in files:
        path = root / file
        if path.is_file():
            try:  # Skip non-text files
                with path.open() as f:
                    text = f.read()
                    for image in [i for i in images if i.is_unused]:
                        if image.name in text:
                            image.occurrences.append(path)
            except UnicodeDecodeError:
                continue

# Identify unused images and sort them for printing
unused_images = [i for i in images if not i.is_unused]
unused_images.sort(key=lambda x: (x.path, x.name))
print(
    f"Out of {len(images)} total images, found {len(unused_images)} unused images occupying {sum(i.disk_usage for i in unused_images):,} bytes on disk.")
[print(f"{i.path}, {i.disk_usage / 1000:.2f} kB") for i in unused_images]

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
