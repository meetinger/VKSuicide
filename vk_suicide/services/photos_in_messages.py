import re
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import Generator

from vk_suicide.services.common import ApiTaskData
from vk_suicide.vk_api_client import VKApiClient


def parse_photos_in_messages_in_file(file_path: str, vk_api_client: VKApiClient) -> Generator[ApiTaskData, None, None]:
    with open(file_path, 'r') as f:
        text = f.read()

    matches_iterator = re.finditer(r'<div class="message".*?<div class="attachment">.*?</div>', text, re.DOTALL)

    msgs_id = []
    for match_obj in matches_iterator:
        match = match_obj.group(0)
        msgs_id.append(re.sub('[^0-9]', '', re.search(r'data-id="\d*"', match).group()))

    def _filter_func(_msg: dict):
        for _attachment in _msg['attachments']:
            if _attachment['type'] == 'photo' and _attachment['photo']['owner_id'] == vk_api_client.user_id:
                return True
        return False

    def _get_messages_with_photos():
        _messages = vk_api_client.execute_method('messages.getById', {'message_ids': ', '.join(msgs_id)})
        return list(filter(_filter_func, _messages['response']['items']))

    msg_batches = [msgs_id[i:i + 100] for i in range(0, len(msgs_id), 100)]

    with ThreadPoolExecutor as executor:
        messages = executor.map(_get_messages_with_photos, msg_batches)

    for msg in messages:
        for attachment in msg['attachments']:
            if attachment['type'] == 'photo':
                photo = attachment['photo']
                yield {'link': 'Owner-id: {} Photo-id: {}'.format(photo['owner_id'], photo['id']),
                       'method': 'photos.delete',
                       'params': {'owner_id': photo['owner_id'],
                                  'photo_id': photo['id']}}


def photos_in_messages_files_iterator(extracted_archive_path: str) -> Generator[Path, None, None]:
    category_dir = Path(extracted_archive_path, 'messages')
    if not category_dir.exists():
        return
    for chat_dir in category_dir.iterdir():
        for file_name in chat_dir.iterdir():
            yield (category_dir / chat_dir / file_name).absolute()
