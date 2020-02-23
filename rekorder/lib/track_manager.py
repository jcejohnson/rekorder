
from .track import Track
from .what import What


class TrackManager:

  @staticmethod
  def playback_instance(tracks, mode):
    return TrackManager(tracks=tracks, mode=mode)

  def __init__(self, *args, **kwargs):
    super().__init__()

    self.mode = kwargs['mode']

    if self.mode == What.RECORD:
      self._tracks = [
          Track(index=n, title=title)
          for n, title in enumerate(['header', 'entry', 'recording', 'exit', 'trailer'])
      ]

    elif self.mode in [What.DESCRIBE, What.PLAYBACK]:
      self._tracks = [
          Track.playback_instance(track, mode=self.mode)
          for track in kwargs['tracks']
      ]

    self._index = 0

  @staticmethod
  def recordable_data(obj):
    return obj._tracks

  @property
  def current(self):
    return self._tracks[self._index]

  @property
  def tracks(self):
    return self._tracks

  @property
  def next(self):
    self._index += 1
    if self._index > len(self._tracks):
      raise Exception("Attempt to access non-existent track.")

  def reset(self):
    self._index = 0
    return self.current()
