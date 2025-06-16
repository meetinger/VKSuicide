import functools
import multiprocessing as mp

from pathlib import Path
from typing import Callable

from vk_suicide.loggers import get_logger, get_worker_logger
from vk_suicide.services.comments import comments_files_iterator, parse_comments_from_file
from vk_suicide.services.common import delete_category_sync
from vk_suicide.services.likes import likes_files_iterator, parse_likes_from_file
from vk_suicide.services.photos_in_albums import photos_in_albums_files_iterator
from vk_suicide.services.photos_in_messages import parse_photos_in_messages_from_file
from vk_suicide.services.wall import wall_files_iterator, parse_wall_posts_from_file
from vk_suicide.vk_api_client import VKApiClient


class ServiceInterface:
    def __init__(self, vk_api_client: VKApiClient,
                 extracted_archive_path: str | Path,
                 progress_monitor_factory: Callable[[str], Callable[[list, mp.Value, mp.Event], None]],
                 get_string: Callable[[str], str] = lambda x: x,
                 log_queue: mp.Queue = None):
        self.vk_api_client = vk_api_client
        self.extracted_archive_path = extracted_archive_path
        self.progress_monitor_factory = progress_monitor_factory
        self.get_string = get_string
        self.log_queue = log_queue
        self.logger = get_worker_logger(log_queue, 'ServiceInterface')

    def delete_likes(self) -> None:
        likes_files = likes_files_iterator(self.extracted_archive_path)
        if likes_files is None:
            return self.logger.warning(self.get_string('likes_files_not_found'))

        delete_category_sync(
            vk_api_client=self.vk_api_client,
            files_iterator=likes_files,
            file_parser=parse_likes_from_file,
            description=self.get_string('deleting_likes'),
        )

        self.logger.info(self.get_string('likes_deleted'))

    def delete_comments(self) -> None:
        files_comments = comments_files_iterator(self.extracted_archive_path)
        if files_comments is None:
            return self.logger.warning(self.get_string('comments_files_not_found'))

        delete_category_sync(
            vk_api_client=self.vk_api_client,
            files_iterator=files_comments,
            file_parser=parse_comments_from_file,
            description=self.get_string('deleting_comments'),
        )

        self.logger.info(self.get_string('comments_deleted'))

    def delete_wall(self) -> None:
        wall_posts_files = wall_files_iterator(self.extracted_archive_path)

        if wall_posts_files is None:
            return self.logger.warning(self.get_string('wall_files_not_found'))

        delete_category_sync(
            vk_api_client=self.vk_api_client,
            files_iterator=wall_posts_files,
            file_parser=parse_wall_posts_from_file,
            description=self.get_string('deleting_wall'),
        )

        self.logger.info(self.get_string('wall_deleted'))

    def delete_photos_in_albums(self):
        photos_in_albums_files = photos_in_albums_files_iterator(self.extracted_archive_path)
        if photos_in_albums_files is None:
            return self.logger.warning(self.get_string('photos_in_albums_files_not_found'))

        delete_category_sync(
            vk_api_client=self.vk_api_client,
            files_iterator=photos_in_albums_files,
            file_parser=parse_likes_from_file,
            description=self.get_string('deleting_photos_in_albums')
        )

        self.logger.info(self.get_string('photos_in_albums_deleted'))

    def delete_photos_in_messages(self):
        photos_in_messages_files = photos_in_albums_files_iterator(self.extracted_archive_path)
        if photos_in_messages_files is None:
            return self.logger.warning(self.get_string('photos_in_messages_files_not_found'))

        delete_category_sync(
            vk_api_client=self.vk_api_client,
            files_iterator=photos_in_messages_files,
            file_parser=functools.partial(parse_photos_in_messages_from_file, vk_api_client=self.vk_api_client),
            description=self.get_string('deleting_photos_in_messages')
        )

        self.logger.info(self.get_string('photos_in_messages_deleted'))
