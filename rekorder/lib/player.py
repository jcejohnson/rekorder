
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
    self._things = {}

  def describe(self):
    '''Describe a recording.
    '''

    recorder = None
    tracks = self._cassette.playback()
    for track in tracks:  # [{header:...}, {recording:...}, {trailer:...}]
      for track_name, tunes in track.items():  # {track_name: [{...}, ...]}
        print(track_name)
        if not tunes:
          print("  None")
          continue
        for tune in tunes:  # [{data: {...}, device: {...}, ...}, {...}]
          # Figure out the class type
          device = tune['device']
          cls = self.get_device(device['module'], device['class'])
          # Ask the class to construct a playable representation of itself.
          # This may be an instance of cls or something else.
          device = cls.playback_instance(
              cls,                 # The class type making the request
              mode=What.DESCRIBE,  # What we want the thing to do
              tune=tune            # Data recorded by the cls instance
          )
          # The Recorder class is special. When we find it, we need to keep
          # a reference for the upcoming classes. There should only ever be
          # one Recorder in any input file.
          if cls == Recorder:
            if recorder:
              raise Exception("To many recorders")
          print("  {}".format(device.describe_device()))

    return

  def get_device(self, module, thing, file=None, **kwargs):
    signature = str(file) + '.' + module + '.' + thing
    if signature in self._things:
      return self._things[signature]
    # print("Import [{}]".format(module))
    module = importlib.import_module(module)
    #
    # This doesn't work for loading functions.
    # We need to save the file name that contains
    # the function too.
    #
    # print(module)
    # print(dir(module))
    thing = getattr(module, thing)
    self._things[signature] = thing
    return self._things[signature]
