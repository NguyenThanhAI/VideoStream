import os
import argparse
from datetime import datetime
from multiprocessing import Process, Queue
from threading import Thread
import cv2


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_source", help="Video source")
    args = parser.parse_args()
    return args


class MultiProcessedVideoStream(object):
    def __init__(self, video_source, queue):
        self.cap = cv2.VideoCapture(video_source)
        #self.cap.set(cv2.CAP_PROP_POS_FRAMES, 89000)
        self.queue = queue
        self.frame_id = 0
        self.stopped = False
        print("Init multiprocess video stream")

    def start(self):
        self.process = Thread(target=self.update, args=()) # Không thể dùng Process được :( :( :( :(
        self.process.daemon = True
        print("Start multiprocess video stream")
        self.process.start()

    def update(self):
        while not self.stopped:
            if not self.queue.full():
                ret, frame = self.cap.read()
                time_stamp = datetime.now()
                if not ret:
                    self.stop()
                self.queue.put((self.frame_id, time_stamp, frame))
                print("Thread, {}, {}".format(os.getpid(), os.getppid()))
                self.frame_id += 1

    def stop(self):
        self.stopped = True
        self.process.join()


class MainProcess(Process):
    def __init__(self, queue):
        super(MainProcess, self).__init__()
        self.input_queue = queue
        self.stopped = False
        print("Init mainprocess")

    def run(self):
        while not self.stopped:
            if not self.input_queue.empty():
                self.frame_id, self.time_stamp, self.frame = self.input_queue.get()
                self.display()
                print("Process, {}, {}, {}".format(os.getpid(), os.getppid(), self.input_queue.qsize()))
            #else:
            #    print("Stop")
            #    self.stop()

    def display(self):
        cv2.imshow("Frame", self.frame)
        cv2.waitKey(1)

    def stop(self):
        self.stopped = True


if __name__ == '__main__':
    args = get_args()

    queue = Queue(maxsize=1000)
    print("Start, {}, {}".format(os.getpid(), os.getppid()))
    videostream = MultiProcessedVideoStream(video_source=args.video_source, queue=queue)
    mainprocess = MainProcess(queue=queue)
    videostream.start()
    mainprocess.start()
    mainprocess.join()