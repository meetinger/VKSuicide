import os
import re
import time
import queue
import logging
import multiprocessing as mp
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, Any, Generator

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


def _process_directory(cur_dir_name: str, extracted_archive_path: str, vk_api_client: Any,
                       total_work_count: mp.Value, total_lock: mp.Lock, progress_queue: mp.Queue) -> None:
    dir_path = os.path.join(extracted_archive_path, cur_dir_name)
    likes_tasks = []

    for file_name in os.listdir(dir_path):
        tasks_in_file = list(_parse_likes_in_file(extracted_archive_path, cur_dir_name, file_name))
        with total_lock:
            total_work_count.value += len(tasks_in_file)
        likes_tasks.extend(tasks_in_file)

    def execute_task(task: dict) -> None:
        logger.info(f'Deleting like {task["link"]}')
        vk_api_client.execute_method(task['method'], task['params'])
        progress_queue.put(1)

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(execute_task, likes_tasks))


def _progress_monitor(progress_queue: mp.Queue, total_work_count: mp.Value,
                     progress_callback: Callable[[int, int, str], None],
                     done_event: mp.Event) -> None:
    processed = 0
    while True:
        try:
            progress_queue.get(timeout=0.1)
            processed += 1
            progress_callback(processed, total_work_count.value, 'Deleting likes...')
        except queue.Empty:
            if done_event.is_set() and progress_queue.empty():
                break
            time.sleep(0.1)


def delete_likes(vk_api_client: Any, extracted_archive_path: str,
                 progress_monitor: Callable[[mp.Queue, mp.Value, mp.Event], None],) -> None:

    likes_dir = os.path.join(extracted_archive_path, 'likes')
    if not os.path.isdir(likes_dir):
        logger.error("Директория 'likes' не найдена.")
        return

    likes_dir_list = os.listdir(likes_dir)

    manager = mp.Manager()
    progress_queue = manager.Queue()
    total_work_count = manager.Value('i', 0)
    total_lock = manager.Lock()
    done_event = manager.Event()

    monitor_thread = threading.Thread(
        target=progress_monitor,
        args=(progress_queue, total_work_count, done_event)
    )
    monitor_thread.start()

    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(
                _process_directory,
                cur_dir_name, extracted_archive_path, vk_api_client,
                total_work_count, total_lock, progress_queue
            )
            for cur_dir_name in likes_dir_list
        ]
        for future in futures:
            future.result()

    done_event.set()
    monitor_thread.join()