
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

    else:
      raise Exception("Unsupported mode [{}]".format(self.mode))

    self.reset()

  @staticmethod
  def recordable_data(obj):
    return obj._tracks

  def __iter__(self):
    self._index = 0
    return self

  def __next__(self):
    was = self.current_track.title if self.current_track else ''
    if self._index < self._max:
      self.current_track = self._tracks[self._index]
      self._index += 1
      return self.current_track
    else:
      raise StopIteration

  def set_track(self, new_track):
    while self.current_track and self.current_track.title != new_track:
      next(self)

  @property
  def tracks(self):
    return self

  @property
  def next(self):
    return self.__next__()

  def reset(self):
    self.current_track = None
    self._index = 0
    self._max = len(self._tracks)
    return self.next
