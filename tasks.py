import sys, logging, multiprocessing, time, traceback
from logging.handlers import TimedRotatingFileHandler

from celery import Celery
from celery.utils.log import get_task_logger
from celery.signals import after_setup_logger

app = Celery()
app.config_from_object("config")  # 指定配置文件

logger = get_task_logger(__name__)
queue = multiprocessing.Queue(-1)


def listener_configurer():
    logger = logging.getLogger()
    h = TimedRotatingFileHandler(filename='workers.log', when='M', backupCount=7)
    f = logging.Formatter('%(asctime)s %(processName)-18s %(name)s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    logger.addHandler(h)


def listener_process(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            while record is None:
                time.sleep(1)
                record = queue.get()
            logger = logging.getLogger()
            logger.handle(record)
        except Exception:
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


@app.task
def taskA(x, y):
    old_outs = sys.stdout, sys.stderr
    rlevel = app.conf.worker_redirect_stdouts_level
    try:
        app.log.redirect_stdouts_to_logger(logger, rlevel)
        print('Adding {0} + {1}'.format(x, y))
        return x + y
    finally:
        sys.stdout, sys.stderr = old_outs


@app.task
def taskB(x, y, z):
    old_outs = sys.stdout, sys.stderr
    rlevel = app.conf.worker_redirect_stdouts_level
    try:
        app.log.redirect_stdouts_to_logger(logger, rlevel)
        print('Adding {0} + {1} + {2}'.format(x, y, z))
        return x + y + z
    finally:
        sys.stdout, sys.stderr = old_outs


@after_setup_logger.connect
def setup_loggers(**kwargs):
    f = logging.Formatter("%(message)s")
    h = logging.handlers.QueueHandler(queue)
    h.setFormatter(f)
    logger.setLevel(logging.INFO)
    logger.addHandler(h)
    listener = multiprocessing.Process(target=listener_process, args=(queue, listener_configurer))
    listener.start()
