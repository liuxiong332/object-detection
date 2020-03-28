# from model import object_detection

# object_detection.ModelRunner().run()

from device_service import device_manager

if __name__ == '__main__':
  dm = device_manager.DeviceManager()
  dm.add_device("1")

  dm.join()