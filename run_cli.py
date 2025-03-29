import os
import zipfile
from enum import IntEnum

from project_root import PROJECT_ROOT
from vk_suicide.inputs import get_args, get_args_inline
from vk_suicide.loggers import get_logger
from vk_suicide.services.common import progress_callback_cli_factory
from vk_suicide.services.interface import ServiceInterface
from vk_suicide.translations import get_string
from vk_suicide.vk_api_client import VKApiClient

CAPTCHA_SOLVER = True
try:
    from vk_captcha import VkCaptchaSolver
    CAPTCHA_SOLVER = True
except ImportError as e:
    CAPTCHA_SOLVER = False

logger = get_logger(__name__)

def main():

    language = get_args(num_of_args=1,
                        allowed_args=['ru', 'en'],
                        start_msg=f"{get_string('choose_language', 'ru')}\n{get_string('choose_language', 'en')}:",
                        print_func=logger.info,
                        arg_type=str)[0]

    def _get_s(string_name: str):
        return get_string(string_name, language)

    if CAPTCHA_SOLVER is False:
        do_want_continue = get_args(num_of_args=1,
                                    allowed_args=['yes', 'no'],
                                    start_msg=_get_s('captcha_solver_not_found'),
                                    print_func = logger.warning,
                                    arg_type=str)[0]
        if do_want_continue != 'yes':
            return

    archive_path = None

    if 'Archive' in os.listdir(PROJECT_ROOT):
        archive_path = PROJECT_ROOT / 'Archive'
        logger.info(_get_s('dir_archive_detected'))
    elif 'Archive.zip' in os.listdir(PROJECT_ROOT):
        archive_path = PROJECT_ROOT / 'Archive.zip'
        is_want_unzip = get_args(num_of_args=1,
                                 allowed_args=['yes', 'no'],
                                 start_msg=_get_s('zip_archive_detected'),
                                 arg_type=str, print_func=logger.info)[0]

        if is_want_unzip == 'no':
            logger.info(_get_s('dir_archive_not_detected'))
            return

        logger.info(_get_s('unzipping_archive'))

        unpacked_archive = PROJECT_ROOT / 'Archive'

        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(unpacked_archive)

        logger.info(_get_s('unzipping_done'))
    else:
        logger.info(_get_s('dir_archive_not_detected'))

    token = get_args(num_of_args=1,
                     start_msg=_get_s('enter_token'),
                     arg_type=str, print_func=logger.info)[0]
    if 'oauth.vk.com' in token:
        token = token.split('access_token=')[-1].split('&expires_in=')[0]



    while not VKApiClient.check_token(token):
        logger.info(_get_s('invalid_token'))
        token = get_args(num_of_args=1,
                                 start_msg=_get_s('enter_token'),
                                 arg_type=str, print_func=logger.info)[0]

        if 'oauth.vk.com' in token:
            token = token.split('access_token=')[-1].split('&expires_in=')[0]

    vk_api_client = VKApiClient(token)

    service_interface = ServiceInterface(vk_api_client, archive_path, progress_callback_cli_factory)

    class DeleteCategory(IntEnum):
        LIKES = 1
        COMMENTS = 2
        WALL = 3
        PHOTOS_IN_MESSAGES = 4
        PHOTOS_IN_ALBUMS = 5

    for_deletion = get_args_inline(num_of_args=-1, allowed_args=[i.value for i in DeleteCategory],
                               start_msg=_get_s('select_for_deletion'), arg_type=int)

    if DeleteCategory.LIKES.value in for_deletion:
        service_interface.delete_likes()

    if DeleteCategory.COMMENTS.value in for_deletion:
        service_interface.delete_comments()

    if DeleteCategory.WALL.value in for_deletion:
        service_interface.delete_wall()

    if DeleteCategory.PHOTOS_IN_MESSAGES.value in for_deletion:
        service_interface.delete_photos_in_messages()

    if DeleteCategory.PHOTOS_IN_ALBUMS.value in for_deletion:
        service_interface.delete_photos_in_albums()







if __name__ == '__main__':
    main()