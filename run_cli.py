import os
import zipfile

from project_root import PROJECT_ROOT
from vk_suicide.inputs import get_args
from vk_suicide.loggers import get_logger
from vk_suicide.vk_api_client import VKApiClient

CAPTCHA_SOLVER = True
try:
    from vk_captcha import VkCaptchaSolver
    CAPTCHA_SOLVER = True
except ImportError:
    CAPTCHA_SOLVER = False

logger = get_logger(__name__)

def main():
    if CAPTCHA_SOLVER is False:
        do_want_continue = get_args(num_of_args=1,
                                    allowed_args=['y', 'n'],
                                    start_msg='Not found vk_captcha module! Continue? y/n',
                                    arg_type=str, print_func=logger.warning)[0]
        if do_want_continue != 'y':
            return

    archive_path = None

    if 'Archive' in os.listdir(PROJECT_ROOT):
        archive_path = PROJECT_ROOT / 'Archive'
        logger.info('Unpacked archive found!')
    elif 'Archive.zip' in os.listdir(PROJECT_ROOT):
        archive_path = PROJECT_ROOT / 'Archive.zip'
        is_want_unzip = get_args(num_of_args=1,
                                 allowed_args=['y', 'n'],
                                 start_msg='Archive.zip found! Unzip? y/n',
                                 arg_type=str, print_func=logger.info)[0]
        if is_want_unzip == 'n':
            logger.info('Archive not unpacked!')
            return
        with zipfile.ZipFile(PROJECT_ROOT / 'Archive.zip', 'r') as zip_ref:
            zip_ref.extractall(PROJECT_ROOT / 'Archive')
        logger.info('Archive unpacked!')
    else:
        logger.info('Archive not found!')

    access_token = get_args(num_of_args=1, allowed_args=lambda token: VKApiClient.check_token(token).get('response', -1) > 0,
                    start_msg=get_string('enter_token', GlobalVars.language), arg_type=str,
                    err_msg=get_string('invalid_token', GlobalVars.language))[0]

    vk_api_client = VKApiClient(access_token)





if __name__ == '__main__':
    main()