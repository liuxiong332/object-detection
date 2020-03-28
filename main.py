# from model import object_detection

# object_detection.ModelRunner().run()

from device_service import device_manager
from http.server import HTTPServer, BaseHTTPRequestHandler
import re

device_manager = device_manager.DeviceManager()


class ServerHTTP(BaseHTTPRequestHandler):

    def do_POST(self):
        print("Get path", self.path)
        search_res = re.search(r"/device/add\?deviceId=(\d+)", self.path)
        if search_res is not None:
            device_manager.add_device(search_res.group(1))
            self.send_response(200, "ok")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        search_res = re.search(r"/device/del\?deviceId=(\d+)", self.path)
        if search_res is not None:
            device_manager.del_device(search_res.group(1))
            self.send_response(200, "ok")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        return self.send_response(500, "unknown command")


if __name__ == '__main__':
    # dm = device_manager.DeviceManager()
    # dm.add_device("1")

    # dm.join()
    http_server = HTTPServer(('', 1999), ServerHTTP)
    print("Server start listen on ", 1999)
    http_server.serve_forever()
    device_manager.join()
