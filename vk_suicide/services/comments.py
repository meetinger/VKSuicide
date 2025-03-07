import re
from pathlib import Path
from typing import Generator


def parse_likes_in_file(extracted_archive_path: str, file_name: str) -> Generator:
    link_regex = r'https://vk.com/[a-z]+[-0-9]+_[0-9]+\?\w+\=[-0-9]+\&*\w*\=*[-0-9]*'

    with open(f'{extracted_archive_path}/comments/{file_name}', 'r') as f:
        text = f.read()

    for match in re.findall(link_regex, text):
        owner_id = re.search(r'[-0-9]+', match).group()
        reply_id = re.search(r'reply=[-0-9]+', match).group()
        thread_id = re.search(r'thread=[-0-9]+', match)
        comment_id = reply_id

        yield {'link': match, 'method': 'wall.deleteComment',
                                                        'params': {'owner_id': int(owner_id),
                                                                   'comment_id': int(comment_id)}}

def comments_files_iterator(extracted_archive_path: str) -> Generator[Path, None, None]:
    category_dir = Path(extracted_archive_path, 'likes')
    if not category_dir.exists():
        return
    for file_name in category_dir.iterdir():
        yield (category_dir / file_name).absolute()
