import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmicloud import *


def concurrency_authentication(global_lock,two_fa_code):
    cli = Client(two_fa_code= two_fa_code, lock=global_lock)
    print("refresh_token:", cli.iam_client.get_refresh_token())
    print("access_token:", cli.iam_client.get_access_token())


def multi_threaded_authentication(two_fa_code):
    from threading import Thread
    from multiprocessing import Lock
    global_lock = Lock()

    threads = []
    for _ in range(5):
        t = Thread(target=concurrency_authentication, args=(global_lock,two_fa_code))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


def multi_process_authentication(two_fa_code):
    from multiprocessing import Process, Manager
    manager = Manager()
    global_lock = manager.Lock()

    processes = []
    for _ in range(4):
        t = Process(target=concurrency_authentication, args=(global_lock,two_fa_code))
        t.start()
        processes.append(t)
        # time.sleep(3)

    for t in processes:
        t.join()



if __name__ == "__main__":

    two_fa_code = "123456"

    multi_process_authentication(two_fa_code)

    multi_threaded_authentication(two_fa_code)
