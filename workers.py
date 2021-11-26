import threading
import time

from GlobalVars import GlobalVars
from utils import progress_bar

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
            GlobalVars.msgs.extend(resp['response']['items'])
            GlobalVars.get_msg_progress = GlobalVars.get_msg_progress + 1
            progress_bar(50, GlobalVars.get_msg_progress, self.msgs_id_len)

