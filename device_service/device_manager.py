
from model import object_detection
from multiprocessing import Process, Pipe


def device_process(conn):
    object_detection.ModelRunner(conn).run()


class DeviceManager:
    def __init__(self):
        self.device_ids = []
        self.tasks = {}
        self.conns = {}

    def add_device(self, device_id):
        print("Start new device", device_id)
        if not hasattr(self, "device_ids"):
            self.device_ids = []
        if device_id not in self.device_ids:
            self.device_ids.append(device_id)
            self.start_task(device_id)

    def del_device(self, device_id):
        print("Will delete device", device_id)
        if device_id in self.device_ids:
            self.conns[device_id].send("quit")
            self.tasks[device_id].join()
            self.conns[device_id].close()
            self.device_ids.remove(device_id)
            del self.conns[device_id]
            del self.tasks[device_id]

    def start_task(self, device_id):
        parent_conn, child_conn = Pipe()
        p = Process(target=device_process, args=(child_conn, ))
        p.start()
        self.tasks[device_id] = p
        self.conns[device_id] = parent_conn
        print("start task", device_id, self.tasks, self.conns)

    def join(self):
        for d in self.device_ids:
            self.del_device(d)
