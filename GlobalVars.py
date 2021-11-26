import threading


class GlobalVars:
    get_msg_progress = 0
    msgs = []
    get_msg_lock = threading.Lock()