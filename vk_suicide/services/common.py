import multiprocessing as mp
import queue
import time
from concurrent.futures import ThreadPoolExecutor

from typing import Generator, Callable, Any

from vk_suicide.loggers import get_logger

logger = get_logger(__name__)


def progress_monitor(progress_queue: mp.Queue, total_work_count: mp.Value,
                     progress_callback: Callable[[int, int, str], None],
                     label: str,
                     done_event: mp.Event) -> None:
    processed = 0
    while True:
        try:
            progress_queue.get(timeout=0.1)
            processed += 1
            progress_callback(processed, total_work_count.value, label)
        except queue.Empty:
            if done_event.is_set() and progress_queue.empty():
                break
            time.sleep(0.1)

def process_file(cur_dir_name: str,
                 file_name: str,
                 likes_dir: str,
                 vk_api_client: Any,
                 file_parser: Callable[[str, str, str], Generator],
                 log_str: str,
                 total_work_count: mp.Value,
                 total_lock: mp.Lock,
                 progress_queue: mp.Queue) -> None:

    tasks = list(file_parser(likes_dir, cur_dir_name, file_name))

    with total_lock:
        total_work_count.value += len(tasks)

    def execute_task(task: dict) -> None:
        logger.info(log_str.format(task['link']))
        vk_api_client.execute_method(task['method'], task['params'])
        progress_queue.put(1)

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(execute_task, tasks))