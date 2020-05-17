from queue import Queue
from threading import Thread, Event
from multiprocessing import Process, Event
# A thread that produces data


def producer(out_q):
    count = 0
    for i in range(100000):
        # Produce some data
        ...
        # Make an (data, event) pair and hand it to the consumer
        evt = Event()
        out_q.put((count, evt))
        ...
        # Wait for the consumer to process the item
        print("Thread 1, {}, {}, {}".format(count, out_q.qsize(), evt.is_set()), end="\n")
        count += 1
        #evt.wait()
        #print("Thread 1 {}".format(evt.is_set()), end="\n")
        if not evt.is_set():
            print("Not set")
        else:
            print("Set")
# A thread that consumes data
def consumer(in_q):
    while True:
        # Get some data
        data, evt = in_q.get()
        # Process the data
        ...
        # Indicate completion
        print("Thread 2, {} {}".format(data, in_q.qsize()), end=" ")
        evt.set()
        print("{}".format(evt.is_set()), end="\n")


if __name__ == '__main__':
    queue = Queue(10)

    thread_1 = Thread(target=producer, args=(queue,))
    thread_2 = Thread(target=consumer, args=(queue,))

    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()