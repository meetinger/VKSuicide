import functools
from pathlib import Path
from typing import Callable

from vk_suicide.loggers import get_logger
from vk_suicide.services.comments import comments_files_iterator, parse_comments_from_file
from vk_suicide.services.common import delete_category
from vk_suicide.services.likes import likes_files_iterator, parse_likes_from_file
from vk_suicide.services.photos_in_albums import photos_in_albums_files_iterator
from vk_suicide.services.photos_in_messages import parse_photos_in_messages_from_file
from vk_suicide.services.wall import wall_files_iterator
from vk_suicide.vk_api_client import VKApiClient

logger = get_logger(__name__)

class ServiceInterface:
    def __init__(self, vk_api_client: VKApiClient, extracted_archive_path: str | Path,
                 progress_monitor_factory: Callable[[str], Callable[[int, int], None]]):
        self.vk_api_client = vk_api_client
        self.extracted_archive_path = extracted_archive_path
        self.progress_monitor_factory = progress_monitor_factory

    def delete_likes(self) -> None:
        likes_files = likes_files_iterator(self.extracted_archive_path)
        if likes_files is None:
            return logger.warning('Likes files in archive not found')

        delete_category(
            vk_api_client=self.vk_api_client,
            files_iterator=likes_files,
            file_parser=parse_likes_from_file,
            progress_monitor=self.progress_monitor_factory('Deleting likes...')
        )

        logger.info('Likes deleted')

    def delete_comments(self) -> None:
        files_comments = comments_files_iterator(self.extracted_archive_path)
        if files_comments is None:
            return logger.warning('Comments files in archive not found')

        delete_category(
            vk_api_client=self.vk_api_client,
            files_iterator=files_comments,
            file_parser=parse_comments_from_file,
            progress_monitor=self.progress_monitor_factory('Deleting comments...')
        )

        logger.info('Comments deleted')

    def delete_wall(self) -> None:
        wall_posts_files = wall_files_iterator(self.extracted_archive_path)

        if wall_posts_files is None:
            return logger.warning('Wall posts files in archive not found')

        delete_category(
            vk_api_client=self.vk_api_client,
            files_iterator=wall_posts_files,
            file_parser=parse_likes_from_file,
            progress_monitor=self.progress_monitor_factory('Deleting wall posts...')
        )

        logger.info('Wall posts deleted')

    def delete_photos_in_albums(self):
        photos_in_albums_files = photos_in_albums_files_iterator(self.extracted_archive_path)
        if photos_in_albums_files is None:
            return logger.warning('Photos in albums files in archive not found')

        delete_category(
            vk_api_client=self.vk_api_client,
            files_iterator=photos_in_albums_files,
            file_parser=parse_likes_from_file,
            progress_monitor=self.progress_monitor_factory('Deleting photos in albums...')
        )

        logger.info('Photos in albums deleted')

    def delete_photos_in_messages(self):
        photos_in_messages_files = photos_in_albums_files_iterator(self.extracted_archive_path)
        if photos_in_messages_files is None:
            return logger.warning('Photos in messages files in archive not found')

        delete_category(
            vk_api_client=self.vk_api_client,
            files_iterator=photos_in_messages_files,
            file_parser=functools.partial(parse_photos_in_messages_from_file, vk_api_client=self.vk_api_client),
            progress_monitor=self.progress_monitor_factory('Deleting photos in messages...')
        )

        logger.info('Photos in messages deleted')
