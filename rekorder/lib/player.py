
from .cassette import Cassette
from .device import Device
from .recorder import Recorder
from .what import What

import importlib


class Player:
  '''Describe and replay recordings.
  '''

  def __init__(self, *args, **kwargs):
    self._cassette = Cassette(*args, **kwargs)

  def describe(self):
    '''Describe a recording.
    '''

    for track in self._cassette.tracks:
      print(track.title)

      if not len(track.tunes):
        print("  None")
        continue

      for tune in track.tunes:
        print("  {}".format(tune.device))

        if isinstance(tune.device, Recorder):
          if self._cassette.recorder:
            raise Exception("Too many recorders")
          self._cassette.recorder = tune.device
