
import time


class Timestamp:

  def __init__(self, *args, **kwargs):
    super().__init__()
    self.time = kwargs.get('time', time.time())
    self.localtime = kwargs.get('localtime', time.asctime(time.localtime(self.time)))

  def __call__(self):
    return self
