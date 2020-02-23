
from .tune import Tune
from .what import What


class Track:

  @staticmethod
  def playback_instance(track, mode):
    return Track(**track, mode=mode)

  @staticmethod
  def recordable_data(obj):
    return {
        'index': obj.index,
        'title': obj.title,
        'tunes': obj.tunes
    }

  def __init__(self, index, title, tunes=None, mode=What.RECORD):
    super().__init__()

    self.mode = mode
    self.index = index
    self.title = title
    self.tunes = [
        Tune.playback_instance(t, self.mode) for t in tunes
    ] if tunes else []

  def add(self, tune):
    self.tunes.append(tune)
