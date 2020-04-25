
from ..tune import Tune
from ..what import What


class Track:
  '''A Track is a collection of Tunes.
  '''

  @staticmethod
  def playback_instance(track, mode):
    return Track(**track, mode=mode)

  @staticmethod
  def recordable_data(obj):
    r = {
        'index': obj.index,
        'title': obj.title,
        'tunes': obj.tunes
    }
    # if obj.sub_track:
    #   r['sub_track'] = Track.recordable_data(obj.sub_track)
    return r

  def __init__(self, index, title, tunes=None, mode=What.RECORD, parent=None):
    super().__init__()

    self.current_tune = None
    self.mode = mode
    self.index = index
    self.title = title
    self.parent = parent
    self.sub_track = None
    self.tunes = [
        Tune.playback_instance(t, mode=self.mode) for t in tunes
    ] if tunes else []
    self.reset()

  def add(self, tune):
    self.tunes.append(tune)

  def reset(self):
    self._iter = iter(self.tunes)
    self.current_tune = None

  def size(self):
    return len(self.tunes)

  def next_tune(self):
    self.current_tune = next(self._iter)
    return self.current_tune
