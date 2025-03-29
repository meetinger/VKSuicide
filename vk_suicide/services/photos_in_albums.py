import re
from pathlib import Path
from typing import Generator

from vk_suicide.services.common import ApiTaskData
from vk_suicide.utils import AutoOpen


def parse_photos_in_albums_from_file(file_path: str) -> Generator[ApiTaskData, None, None]:
    with AutoOpen(file_path) as f:
        text = f.read()

    photos_links = set(re.findall(r'https://vk.com/photo\d+_\d+', text))

    for link in photos_links:
        owner_id, photo_id = re.findall(r'\d+', link)
        yield {'link': link, 'method': 'photos.delete',
               'params': {'owner_id': owner_id,
                          'photo_id': photo_id}}

def photos_in_albums_files_iterator(extracted_archive_path: str) -> Generator[Path, None, None]:
    category_dir = Path(extracted_archive_path, 'photos', 'photo-albums')
    if not category_dir.exists():
        return
    for album_file in category_dir.iterdir():
        yield (category_dir / album_file).absolute()
