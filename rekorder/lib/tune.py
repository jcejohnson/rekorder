
import copy

from . import util
from .timestamp import Timestamp
from .what import What
from .when import When


class Tune:
  '''Tune captures Device details, the Notes created by the Device and
      a timestamp.
  '''

  @staticmethod
  def playback_instance(tune, mode):
    if isinstance(tune, Tune):
      tune.mode = mode
      return tune

    cls = util.load_class(tune['device'])
    when = tune['when'] if 'when' in tune else None
    timestamp = Timestamp.playback_instance(tune['timestamp'], mode=mode)
    device = cls.playback_instance(cls=cls,
                                   mode=mode,
                                   timestamp=timestamp,
                                   when=when,
                                   **tune['notes'])
    return Tune(device=device,
                mode=mode,
                notes=tune['notes'],
                timestamp=timestamp,
                when=when
                )

  @staticmethod
  def recordable_data(obj):
    '''Used by Cassette when recording `obj` to the output file.
    '''

    notes = {}
    for key, value in obj.notes.items():
      # TODO - Make this smarter.
      if value == None:
        notes[key] = value
      elif isinstance(value, dict):
        notes[key] = value
      elif isinstance(value, list) or isinstance(value, set) or isinstance(value, tuple):
        notes[key] = list(value)
      elif isinstance(value, int) or isinstance(value, float) or isinstance(value, str):
        notes[key] = value
      else:
        notes[key] = str(value)

    r = {
        'device': {
            'module': obj.device.__class__.__module__,
            'class': obj.device.__class__.__name__
        },
        'notes': notes,
        'timestamp': obj.timestamp
    }
    if obj.when:
      r.update({'when': obj.when})
    return r

  def __init__(self, device, notes, when=When.NA, timestamp=None, mode=What.RECORD):

    self.mode = mode
    self.device = device
    self.when = when
    self.timestamp = timestamp if timestamp else Timestamp()

    # Bugfix: If mutable parameters change during function invocation
    #         MethodParameters recorded the new/changed value for both before
    #         and after.
    # We need to make a deep copy of the notes in case they change after this.
    # For instance, if the notes represent function parameters it is possible
    # that they could change during function invocation.
    self.notes = copy.deepcopy(notes)

    from .device import Device
    if self.device and not isinstance(self.device, Device):
      raise Exception("[{}] is must be a Device".format(self.device))

  def playback(self, *args, **kwargs):
    return self.device.playback(*args, **kwargs)
