import os
from threading import Thread, Lock
from multiprocessing import Process, Lock, Queue
#from frame_queue import Queue

queue = Queue(maxsize=1000)
lock = Lock()


def function_1():
    for i in range(10000000):
        lock.acquire()
        if not queue.full():
            queue.put(i)
            print("Thread 1, {}, {}, {}".format(i, os.getpid(), os.getppid()))
        lock.release()


def function_2():
    while True:
        lock.acquire()
        if not queue.empty():
            i = queue.get()
            print("Thread 2, {}, {}, {}".format(i, os.getpid(), os.getppid()))
        #else:
        #    print("Break")
        #    break
        lock.release()


thread_1 = Thread(target=function_1, args=())
thread_2 = Thread(target=function_2, args=())

thread_1.start()
thread_2.start()
thread_1.join()
thread_2.join()