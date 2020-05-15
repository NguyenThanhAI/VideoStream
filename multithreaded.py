import os
import argparse
from datetime import datetime
from threading import Thread, Lock
from queue import Queue
import cv2


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_source", help="Video source")
    args = parser.parse_args()
    return args


class MultiThreadedVideoStream(object):
    def __init__(self, source, queue, lock):
        self.cap = cv2.VideoCapture(source)
        self.queue = queue
        self.lock = lock
        self.frame_id = 0
        self.stopped = False
        print("Init multithread video stream")

    def start(self):
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        print("Start multithread video stream")
        self.thread.start()

    def update(self):
        while not self.stopped:
            self.lock.acquire()
            if not self.queue.full():
                ret, frame = self.cap.read()
                time_stamp = datetime.now()
                if not ret:
                    self.stop()
                self.queue.put((self.frame_id, time_stamp, frame))
                print("Thread_1, {}, {}, {}".format(ret, frame.shape, self.frame_id))
                self.frame_id += 1
            self.lock.release()

    def stop(self):
        self.stopped = True
        self.thread.join()


class MainThread(Thread):
    def __init__(self, queue, lock):
        super(MainThread, self).__init__()
        self.input_queue = queue
        self.lock = lock
        self.stopped = False
        print("Init mainthread")

    def run(self):
        while not self.stopped:
            self.lock.acquire()
            if not self.input_queue.empty():
                self.frame_id, self.time_stamp, self.frame = self.input_queue.get()
                self.display()
            self.lock.release()
            print("Thread_2, {}, {}, {}".format(self.frame_id, self.time_stamp.strftime("%m/%d/%Y, %H:%M:%S"), self.frame.shape))

    def display(self):
        cv2.imshow("Frame", self.frame)
        cv2.waitKey(1)

    def stop(self):
        self.stopped = True


if __name__ == '__main__':
    args = get_args()
    queue = Queue(maxsize=100)
    lock = Lock()

    videostream = MultiThreadedVideoStream(source=args.video_source, queue=queue, lock=lock)
    mainthread = MainThread(queue=queue, lock=lock)

    videostream.start()
    mainthread.start()

    mainthread.join()
