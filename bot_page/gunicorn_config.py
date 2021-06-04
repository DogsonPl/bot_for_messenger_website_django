from multiprocessing import shared_memory, cpu_count

command = "/root/django_env/bin/gunicorn"
pythonpath = "/root/django_env/lib/python3.8/site-packages"
bind = "0.0.0.0:8000"
workers = cpu_count()*2+1

reload = True

shared_memory = shared_memory.ShareableList([0, 0, 1e10])
"""
:var shared_memory[0] -> tells if django cache started 
:var shared_memory[1] --> tells if scheduler tasks are running
:var shared_memory[2] --> id of worker which is running scheduler tasks
"""


def post_worker_init(worker):
    if not shared_memory[0]:
        from utils import statistic_data
        shared_memory[0] = 1
        statistic_data.init()
    if not shared_memory[1]:
        shared_memory[1] = 1
        shared_memory[2] = worker.pid
        from utils import scheduler
        scheduler.init()
    else:
        print("Scheduler already started")


def worker_abort(worker):
    if worker.pid == shared_memory[2]:
        shared_memory[1] = 0


def on_exit(server):
    shared_memory.shm.close()
    shared_memory.shm.unlink()
