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


def include_file_in_search(local_path: Path) -> bool:
    return (local_path.is_file()
            and not local_path.name.startswith(".")
            and local_path.suffix not in [".plist", ".md", ".lock", ".pbxproj", ".js"]
            and local_path.name not in ["Podfile"])


def print_unusual_locations(local_images: List[Image]):
    for local_image in local_images:
        if local_image.occurrences and local_image.occurrences[0].suffix not in [".swift", ".m", ".xib", ".storyboard"]:
            print(f"{local_image.path}, {local_image.occurrences[0]}")


def print_all_images(local_images: List[Image]):
    for local_image in local_images:
        print(f"{local_image.path}, {str(local_image.occurrences[0]) if local_image.occurrences else None}")


def print_unused_images(local_images: List[Image]):
    for local_image in local_images:
        if local_image.is_unused:
            print(f"{local_image.path}, {str(local_image.occurrences[0]) if local_image.occurrences else None}")


start_time = time.time()
project_root = Path.home().joinpath("work/ios")
images = [Image(p=entry) for entry in project_root.rglob("*.imageset") if "Pods" not in entry.parts]

# Search for occurrence of each image in all files
for root, dirs, files in project_root.walk():
    dirs[:] = [d for d in dirs if include_dir_in_search(d)]
    for file in files:
        path = root / file
        if include_file_in_search(path):
            try:
                with path.open() as f:
                    text = f.read()
                    for image in [i for i in images if i.is_unused]:
                        if f'"{image.name}"' in text:
                            image.occurrences.append(path)
            except UnicodeDecodeError:
                continue  # Skip non-text files

# Identify unused images and sort them for printing
unused_images = [i for i in images if i.is_unused]
print(
    f"Total images: {len(images)}, unused: {len(unused_images)}, occupying {sum(i.disk_usage for i in unused_images):,} bytes on disk.")

print_unusual_locations(images)

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
