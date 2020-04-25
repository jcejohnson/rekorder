
from ..what import What

from .track import Track


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

    self.current_track = None
    self.reset()

  @staticmethod
  def recordable_data(obj):
    return obj._tracks

  def __iter__(self):
    self._index = 0
    return self

  def __next__(self):
    self._check_state()
    was = self.current_track.title if self.current_track else ''
    if self._index < self._max:
      self.current_track = self._tracks[self._index]
      self._index += 1
      return self.current_track
    else:
      raise StopIteration

  def set_track(self, new_track):
    self._check_state()
    while self.current_track and self.current_track.title != new_track:
      next(self)

  def sub_track_begin(self, new_sub_track):
    sub_track = Track(index=self.current_track.index * 10, title=new_sub_track, parent=self.current_track)
    # self.current_track.sub_track = sub_track
    self.current_track = sub_track
    return self.current_track

  def sub_track_conclude(self, new_sub_track):
    self.current_track = self.current_track.parent
    return self.current_track

  @property
  def tracks(self):
    return self

  @property
  def next(self):
    return self.__next__()

  def reset(self):
    self._check_state()
    self.current_track = None
    self._index = 0
    self._max = len(self._tracks)
    return self.next

  def _check_state(self):
    if not self.current_track:
      return
    if self.current_track.parent:
      raise Exception("Illegal state.")
