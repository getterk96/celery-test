from tasks import *
import time

if __name__ == '__main__':
    i = 1
    while 1:
        time.sleep(1)
        if i % 2 == 0:
            taskA.delay(i, i + 1)
        else:
            taskB.delay(i, i + 1, i + 2)
        i += 1