import threading
import time

from GlobalVars import GlobalVars
from translations import get_string
from utils import progress_bar


def filter_func(msg):
    for attachment in msg['attachments']:
        if attachment['type'] == 'photo' and attachment['photo']['owner_id'] == GlobalVars.user_id:
            return True
    return False


class getMsgWorker(threading.Thread):
    def __init__(self, vk_api, msgs_id_batches: list, msgs_id_len):
        super().__init__()
        self.vk_api = vk_api
        self.msg_batches = msgs_id_batches
        self.msgs_id_len = msgs_id_len

    def run(self) -> None:
        for batch in self.msg_batches:
            resp = self.vk_api.execute_method('messages.getById', {'message_ids': ', '.join(batch)})
            while 'error' in resp:
                time.sleep(1)
                resp = self.vk_api.execute_method('messages.getById', {'message_ids': ', '.join(batch)})
            filtered = list(filter(filter_func, resp['response']['items']))
            GlobalVars.get_msg_lock.acquire()
            try:
                GlobalVars.msgs.extend(filtered)
                GlobalVars.get_msg_progress = GlobalVars.get_msg_progress + 1
                progress_bar(50, GlobalVars.get_msg_progress, self.msgs_id_len, additional_str=get_string('getting_list_of_msg', GlobalVars.language))
            finally:
                GlobalVars.get_msg_lock.release()
