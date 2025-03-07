import os
import re
import logging
import multiprocessing as mp
import threading
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from typing import Callable, Any, Generator

from vk_suicide.services.common import process_file

logger = logging.getLogger(__name__)


def _compile_link_regex(content_type: str, has_modifier: bool) -> re.Pattern:
    if has_modifier:
        pattern = rf'https://vk.com/{content_type}[-0-9]+_[0-9]+\?\w+\=[-0-9]+'
    else:
        pattern = rf'https://vk.com/{content_type}[-0-9]+_[0-9]+'
    return re.compile(pattern)


def _parse_likes_in_file(extracted_archive_path: str, cur_dir_name: str, file_name: str) -> Generator[dict, None, None]:
    parts = cur_dir_name.split('_')
    content_type = parts[0]
    has_modifier = len(parts) > 1

    if content_type == 'wall':
        content_type = 'post'

    regex = _compile_link_regex(content_type, has_modifier)
    file_path = os.path.join(extracted_archive_path, cur_dir_name, file_name)

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    for match in regex.findall(text):
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

def delete_likes(vk_api_client: Any, extracted_archive_path: str,
                 progress_monitor: Callable[[mp.Queue, mp.Value, mp.Event], None]) -> None:


    likes_dir = os.path.join(extracted_archive_path, 'likes')
    if not os.path.isdir(likes_dir):
        logger.error("Директория 'likes' не найдена.")
        return

    file_tasks = []
    for cur_dir_name in os.listdir(likes_dir):
        cur_dir_path = os.path.join(likes_dir, cur_dir_name)
        if os.path.isdir(cur_dir_path):
            for file_name in os.listdir(cur_dir_path):
                file_tasks.append((cur_dir_name, file_name))

    manager = mp.Manager()
    progress_queue = manager.Queue()
    total_work_count = manager.Value('i', 0)
    total_lock = manager.Lock()
    done_event = manager.Event()

    monitor_thread = threading.Thread(
        target=partial(progress_monitor, label='Deleting likes...'),
        args=(progress_queue, total_work_count, done_event)
    )
    monitor_thread.start()

    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(
                process_file,
                cur_dir_name,
                file_name,
                likes_dir,
                vk_api_client,
                _parse_likes_in_file,
                'Deleting like: {}',
                total_work_count,
                total_lock,
                progress_queue
            )
            for (cur_dir_name, file_name) in file_tasks
        ]
        for future in futures:
            future.result()

    done_event.set()
    monitor_thread.join()