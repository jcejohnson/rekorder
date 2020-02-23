
import time


class Timestamp:

  @staticmethod
  def playback_instance(*args, **kwargs):
    return Timestamp(*args, **kwargs)

  def __init__(self, *args, **kwargs):
    super().__init__()
    self.time = kwargs.get('time', time.time())
    self.localtime = kwargs.get('localtime', time.asctime(time.localtime(self.time)))

  def __call__(self):
    return self

  @staticmethod
  def recordable_data(obj):
    return {
        'time': obj.time,
        'localtime': obj.localtime
    }
