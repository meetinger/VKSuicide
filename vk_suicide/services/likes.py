import os
import re
import logging
from pathlib import Path
from typing import  Generator

from vk_suicide.services.common import ApiTaskData

logger = logging.getLogger(__name__)

def parse_likes_from_file(file_path: str | Path) -> Generator[ApiTaskData, None, None]:
    file_path = Path(file_path)

    likes_dir, file_name = file_path.parts[-2], file_path.name
    parts = likes_dir.split('_')
    content_type = parts[0]
    has_modifier = len(parts) > 1

    if content_type == 'wall':
        content_type = 'post'

    if has_modifier:
        regex = rf'https://vk.com/{content_type}[-0-9]+_[0-9]+\?\w+\=[-0-9]+'
    else:
        regex = rf'https://vk.com/{content_type}[-0-9]+_[0-9]+'

    regex = re.compile(regex)

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    for match_obj in regex.finditer(text):
        match = match_obj.group(0)
        owner_match = re.search(r'-?\d+', match)
        if not owner_match:
            continue
        owner_id = int(owner_match.group())
        if has_modifier:
            item_match = re.search(r'\?\w+=(-?\d+)', match)
        else:
            item_match = re.search(r'_(-?\d+)', match)
        if item_match:
            item_id = int(item_match.group(1))
            yield {
                'link': match,
                'method': 'likes.delete',
                'params': {
                    'type': content_type,
                    'owner_id': owner_id,
                    'item_id': item_id
                }
            }

def likes_files_iterator(extracted_archive_path: str) -> Generator[Path, None, None]:
    category_dir = Path(extracted_archive_path, 'likes')
    if not category_dir.exists():
        return None
    for content_type_dir in category_dir.iterdir():
        cur_dir_path = category_dir / content_type_dir
        if cur_dir_path.is_dir():
            for file_name in cur_dir_path.iterdir():
                yield (cur_dir_path / file_name).absolute()
