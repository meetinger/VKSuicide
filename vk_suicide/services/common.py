import multiprocessing as mp
import os
import pprint
import threading
import time

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Generator, Callable, Any, TypedDict

from tqdm import tqdm

from vk_suicide.vk_api_client import VKApiClient
from vk_suicide.loggers import get_logger

logger = get_logger(__name__)

class ApiTaskData(TypedDict):
    link: str
    method: str
    params: dict


def process_file(
        vk_api_client: VKApiClient,
        file_path: str,
        file_parser: Callable[[str], Generator],
        total_work_count: mp.Value,
        total_lock: mp.Lock,
        progress_list: list) -> None:

    tasks = list(file_parser(file_path))

    with total_lock:
        total_work_count.value += len(tasks)

    def _execute_task(task: ApiTaskData) -> None:
        logger.debug(f'Processing: {task["link"]}')
        # result = vk_api_client.execute_method(task['method'], task['params'])
        try:
            result = vk_api_client.execute_method(task['method'], task['params'])
            logger.debug(f'Response: {result}')
            if result.get('error'):
                logger.error(f'Error processing {task["link"]}: {result["error"]}')
        except Exception as e:
            logger.error(f'Error processing {task["link"]}: {e}\nData: {task}')
        progress_list.append(1)

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(_execute_task, tasks))

def delete_category(vk_api_client: Any,
                    files_iterator: Generator,
                    file_parser: Callable[[str], Generator],
                    progress_monitor: Callable[[list, mp.Value, mp.Event], None]) -> None:

    manager = mp.Manager()

    progress_list = manager.list()
    total_work_count = manager.Value('i', 0)
    requests_lock = manager.Lock()
    total_lock = manager.Lock()
    done_event = manager.Event()
    vk_shared_data = manager.dict()
    vk_shared_data.update(vk_api_client.shared_data)

    vk_api_client.shared_data = vk_shared_data
    vk_api_client.lock = requests_lock

    monitor_thread = threading.Thread(
        target=progress_monitor,
        args=(progress_list,
              total_work_count,
              done_event)
    )
    monitor_thread.start()

    files = list(files_iterator)
    process_workers_count = min(len(files), os.cpu_count())

    with ProcessPoolExecutor(max_workers=process_workers_count) as executor:
        futures = [
            executor.submit(
                process_file,

                vk_api_client=vk_api_client,
                file_path=file_path,
                file_parser=file_parser,
                total_work_count=total_work_count,
                total_lock=total_lock,
                progress_list=progress_list
            )
            for file_path in files
        ]
        for future in futures:
            future.result()

    done_event.set()
    monitor_thread.join()

def progress_monitor_cli_factory(description: str) -> Callable[[list, Any, Any], None]:
    pbar = None

    def _progress_callback_cli(progress_list: list, total: mp.Value, done_event: mp.Event) -> None:
        nonlocal pbar

        while not done_event.is_set():
            processed = len(progress_list)
            if pbar is None:
                pbar = tqdm(total=total.value, desc=description, dynamic_ncols=True, leave=True,
                            bar_format="{desc}: |{bar}| {percentage:3.0f}% "
                                       "({n_fmt}/{total_fmt}) "
                                       "[{elapsed}<{remaining}, {rate_fmt}]"
                            )

            pbar.total = total.value
            pbar.update(processed - pbar.n)
            time.sleep(0.1)

        pbar.close()
        pbar = None

    return _progress_callback_cli
