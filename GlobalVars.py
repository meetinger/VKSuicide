import multiprocessing
import threading


class GlobalVars:
    get_msg_progress = 0
    msgs = []
    get_msg_lock = threading.Lock()

    get_msg_id_progress = 0
    msgs_id = []
    get_msg_id_lock = multiprocessing.Lock()