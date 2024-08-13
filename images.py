import time
from pathlib import Path
from typing import List


class ImageOccurrence:
    """
    Represents an occurrence of an image in a file.

    Attributes:
        count (int): The number of times the image occurs in the file.
        file (Path): The file where the image is used.
    """

    def __init__(self, count: int, file: Path):
        self.count = count
        self.file = file

    def __repr__(self):
        return f"count: {self.count}, file: {self.file}"


class Image:
    """
        Represents an image in the project.

        Attributes:
            name (str): The name of the image.
            path (str): The relative path to the image.
            disk_usage (int): The disk usage of the image in bytes.
            occurrences (List[ImageOccurrence]): A list of occurrences of the image in the project.
        """

    def __init__(self, name: str, path: Path, disk_usage: int):
        self.name = name
        self.path = str(path)
        self.disk_usage = disk_usage
        self.occurrences: List[ImageOccurrence] = []

    def __repr__(self):
        return (f"path: {self.path}, name: {self.name}, disk_usage: {self.disk_usage}, "
                f"occurrences: {[sum(o.count for o in self.occurrences)]}")


def occurrences_in_file(path: Path, search_string: str) -> int:
    """
    Counts the occurrences of a search string in a file.

    Args:
        path (Path): The path to the file.
        search_string (str): The string to search for in the file.

    Returns:
        int: The number of occurrences of the search string in the file.
    """
    if path.is_file():
        with path.open() as f:
            return f.read().count(search_string)
    return 0


def disk_usage(path: Path) -> int:
    """
        Calculates the total disk usage of files in a directory.

        Args:
            path (Path): The path to the directory.

        Returns:
            int: The total disk usage of files in the directory in bytes.
        """
    return sum([f.stat().st_size for f in path.rglob("*") if f.is_file()])


start_time = time.time()
project_root = Path.home().joinpath("work/ios/")
imagesRoot = project_root.joinpath("Course Hero/Course Hero Rebranded/Assets/Supporting Files/Images.xcassets")

# For each image-set in the project, create an Image object and add it to the images list.
images = [Image(name=entry.stem, path=entry.relative_to(imagesRoot).parent, disk_usage=disk_usage(entry)) for entry in
          imagesRoot.rglob("*.imageset")]

swift_files = [entry for entry in project_root.rglob("*.swift")]
objective_c_files = [entry for entry in project_root.rglob("*.m")]

# Search for occurrences of each image in all Swift and Objective-C files
print(f"Searching for {len(images)} images in {len(swift_files)} swift and {len(objective_c_files)} objective-c files")
for file in swift_files + objective_c_files:
    for image in images:
        if (count := occurrences_in_file(file, f'"{image.name}"')) > 0:
            image.occurrences.append(ImageOccurrence(count, file))

# Identify unused images and sort them for printing
unused_images = [i for i in images if not i.occurrences]
unused_images.sort(key=lambda x: (x.path, x.name))
print(f"Found {len(unused_images)} unused images occupying {sum(i.disk_usage for i in unused_images):,} bytes on disk.")
[print(i) for i in unused_images]

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
