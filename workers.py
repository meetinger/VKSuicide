import multiprocessing
import re
import threading
import time

from GlobalVars import GlobalVars
from utils import progress_bar


class GetMsgIDWorker(threading.Thread):
    def __init__(self, msg_files, cur_msg_dir, msgs_id_array, msgs_id_lock, msgs_id_progress_counter, len_msg_dirs):
        super().__init__()
        self.msg_files = msg_files
        self.cur_msg_dir = cur_msg_dir
        self.msgs_id_array = msgs_id_array
        self.msgs_id_lock = msgs_id_lock
        self.msgs_id_progress_counter = msgs_id_progress_counter
        self.len_msg_dirs = len_msg_dirs

    def run(self) -> None:
        for cur_file_name in self.msg_files:
            # print('Archive/messages/' + cur_msg_dir + '/' + cur_file_name)
            cur_file = open('Archive/messages/' + self.cur_msg_dir + '/' + cur_file_name, 'r')
            lines = cur_file.readlines()

            text = ''.join(lines)

            matches = re.findall(r'<div class="message".*?<div class="attachment">.*?</div>', text, re.DOTALL)

            tmp = [re.sub('[^0-9]', '', re.search(r'data-id="\d*"', match).group()) for match in matches]

            self.msgs_id_array.extend(tmp)
            self.msgs_id_progress_counter.value = self.msgs_id_progress_counter.value + 1 / len(self.msg_files)
            progress_bar(50, self.msgs_id_progress_counter.value, self.len_msg_dirs)


class GetMsgWorker(threading.Thread):
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
            GlobalVars.get_msg_lock.acquire()
            try:
                GlobalVars.msgs.extend(resp['response']['items'])
                GlobalVars.get_msg_progress = GlobalVars.get_msg_progress + 1
                progress_bar(50, GlobalVars.get_msg_progress, self.msgs_id_len)
            finally:
                GlobalVars.get_msg_lock.release()
