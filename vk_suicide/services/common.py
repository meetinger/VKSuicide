import multiprocessing as mp
import os
import queue
import threading
import time

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Queue
from typing import Generator, Callable, Any, TypedDict

from vk_suicide.vk_api_client import VKApiClient
from vk_suicide.loggers import get_logger

logger = get_logger(__name__)

class _TaskDataParams(TypedDict):
    type: str
    owner_id: int
    item_id: int

class ApiTaskData(TypedDict):
    link: str
    method: str
    params: _TaskDataParams


def progress_monitor_factory(progress_callback: Callable[[int, int], None]) -> Callable[[Queue, Any, Any], None]:

    def _process_monitor(progress_queue: mp.Queue, total_work_count: mp.Value, done_event: mp.Event) -> None:
        processed = 0
        while True:
            try:
                progress_queue.get(timeout=0.1)
                processed += 1
                progress_callback(processed, total_work_count.value)
            except queue.Empty:
                if done_event.is_set() and progress_queue.empty():
                    break
                time.sleep(0.1)

    return _process_monitor


def process_file(
        vk_api_client: VKApiClient,
        file_path: str,
        file_parser: Callable[[str, str, str], Generator],
        total_work_count: mp.Value,
        total_lock: mp.Lock,
        progress_queue: mp.Queue) -> None:

    tasks = list(file_parser(file_path))

    with total_lock:
        total_work_count.value += len(tasks)

    def execute_task(task: ApiTaskData) -> None:
        logger.info(f'Processing: {task["link"]}')
        try:
            vk_api_client.execute_method(task['method'], task['params'])
        except Exception as e:
            logger.error(f'Error processing {task["link"]}: {e}\nData: {task}')
        progress_queue.put(1)

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(execute_task, tasks))


def delete_category(vk_api_client: Any,
                    files_iterator: Callable[[], Generator],
                    file_parser: Callable[[str, str, str], Generator],
                    progress_monitor: Callable[[mp.Queue, mp.Value, mp.Event], None]) -> None:

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

    files = list(files_iterator())
    process_workers_count = min(len(files), os.cpu_count())

    with ProcessPoolExecutor(max_workers=process_workers_count) as executor:
        futures = [
            executor.submit(
                fn=process_file,

                vk_api_client=vk_api_client,
                file_path=file_path,
                file_parser=file_parser,
                total_work_count=total_work_count,
                total_lock=total_lock,
                progress_queue=progress_queue
            )
            for file_path in files
        ]
        for future in futures:
            future.result()

    done_event.set()
    monitor_thread.join()