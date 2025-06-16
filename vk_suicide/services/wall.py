import re
from pathlib import Path
from typing import Generator

from vk_suicide.services.common import ApiTaskData
from vk_suicide.utils import AutoOpen


def parse_wall_posts_from_file(file_path: str) -> Generator[ApiTaskData, None, None]:
    with AutoOpen(file_path) as f:
        text = f.read()

    for match_obj in set(re.finditer(r'https://vk.com/wall[-0-9]+_[0-9]+', text)):
        match = match_obj.group(0)
        owner_id = re.search('[-0-9]+', match).group()
        post_id = re.sub('[^0-9]', '', re.search('_[-0-9]+', match).group())

        yield {'link': match, 'method': 'wall.delete',
               'params': {'owner_id': int(owner_id), 'post_id': int(post_id)}}


def wall_files_iterator(extracted_archive_path: str) -> Generator[Path, None, None]:
    category_dir = Path(extracted_archive_path, 'wall')
    for path in category_dir.rglob('*'):
        if path.is_file():
            yield path.absolute()