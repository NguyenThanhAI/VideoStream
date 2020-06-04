import os
import argparse
import time
from datetime import datetime
from multiprocessing import Process, Queue
from threading import Thread
import cv2
from detector import Detector


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_source", help="Video source")
    args = parser.parse_args()
    return args


class MultiProcessedVideoStream(object):
    def __init__(self, video_source, queue):
        self.cap = cv2.VideoCapture(video_source)
        #self.cap.set(cv2.CAP_PROP_POS_FRAMES, 70000)
        self.queue = queue
        self.frame_id = 0
        self.stopped = False
        print("Init multiprocess video stream")

    def start(self):
        self.process = Thread(target=self.update, args=()) # Không thể dùng Process được :( :( :( :(
        #self.process.daemon = True
        print("Start multiprocess video stream")
        self.process.start()
        #self.process.join() # Thêm join vào process get frame không chạy được :( :( :(

    def update(self):
        while not self.stopped:
            if not self.queue.full():
                ret, frame = self.cap.read()
                time_stamp = datetime.now()
                if not ret:
                    self.stop()
                self.queue.put((self.frame_id, time_stamp, frame))
                #print("Thread stream, {}, {}, {}".format(os.getpid(), os.getppid(), self.queue.qsize()))
                self.frame_id += 1

    def stop(self):
        self.stopped = True
        #self.process.join() # Chú ý vị trí đặt join()


class DetectProcess(Process):
    def __init__(self, frame_queue, bbox_queue):
        super(DetectProcess, self).__init__()
        self.input_queue = frame_queue
        self.output_queue = bbox_queue
        self.stopped = False
        #self.detector = Detector()
        print("Init detect process, {}".format(os.getpid()))
        #self.process = Process(target=self.log, args=())
        #self.process.daemon = True
        #self.process.start()

    def run(self):
        detector = Detector()
        while not self.stopped:
            if not self.input_queue.empty():
                #try:
                self.frame_id, self.time_stamp, self.frame = self.input_queue.get(timeout=None)
                print("Process detecting")
                bboxes = detector(frame=self.frame)
                print("Process detected")
                for bbox in bboxes:
                    x_min, y_min, x_max, y_max = bbox
                    cv2.rectangle(self.frame, (x_min, y_min), (x_max, y_max), (255, 0, 0))
                self.display()
                print("Process detecting, {}, {}, {}".format(os.getpid(), os.getppid(), self.input_queue.qsize()))
                #except:
                #    print("Exit")
                #    self.stop()
            #else:
            #    print("Stop")
            #    self.stop()

    def display(self):
        cv2.imshow("Detection", self.frame)
        cv2.waitKey(1)

    def stop(self):
        self.stopped = True
        #self.join()

    def log(self):
        while True:
            print("This is a subprocess, {}, {}".format(os.getpid(), os.getppid()))


class GetFrameProcess(Process):
    def __init__(self, frame_queue):
        super(GetFrameProcess, self).__init__()
        self.input_queue = frame_queue
        self.stopped = False
        #self.daemon = True

    def run(self):
        while not self.stopped:
            if not self.input_queue.empty():
                try:
                    self.frame_id, self.time_stamp, self.frame = self.input_queue.get(timeout=None)
                    self.display()
                    #print("Process get frame, {}, {}, {}".format(os.getpid(), os.getppid(), self.input_queue.qsize()))
                except:
                    print("Time out")
                    self.stop()

    def display(self):
        cv2.imshow("Frame", self.frame)
        cv2.waitKey(1)

    def stop(self):
        self.stopped = True
        #self.join()

    def log(self):
        while True:
            print("This is a subprocess, {}, {}".format(os.getpid(), os.getppid()))


class TrackProcess(Process):
    def __init__(self, frame_queue, bbox_queue):
        super(TrackProcess, self).__init__()
        self.frame_queue = frame_queue
        self.bbox_queue = bbox_queue



if __name__ == '__main__':
    args = get_args()

    frame_queue = Queue(maxsize=5)
    bbox_queue = Queue(maxsize=1)
    print("Start, {}, {}".format(os.getpid(), os.getppid()))
    videostream = MultiProcessedVideoStream(video_source=args.video_source, queue=frame_queue)
    detectprocess = DetectProcess(frame_queue=frame_queue, bbox_queue=bbox_queue)
    getframe = GetFrameProcess(frame_queue=frame_queue)
    detectprocess.start()
    #time.sleep(50)
    videostream.start()
    getframe.start()
    detectprocess.join() # Huhu, nếu uncomment hai dòng này thì các process sẽ không chạy làm chương trình bị treo
    getframe.join()