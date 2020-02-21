
import logging

from .what import What

logger = logging.getLogger(__name__)


class Device:
  '''A thing that can be recorded, played back or described.
  '''

  def __init__(self, *args, **kwargs):

    if not kwargs.get('mode', None) and not kwargs.get('recorder', None):
      raise Exception("Programmer error")

    # Set the mode (if provided)
    self.mode = kwargs.get('mode', None)
    self.recorder = kwargs.get('recorder', None)

    if not self.mode:
      if not self.recorder:
        raise Exception("Recorder required when mode is not provided.")

      self.mode = self.recorder.mode

      # If we were given a mode it must match the recorder's mode
      if self.mode != self.recorder.mode:
        raise Exception("Mismatch between our mode [{}]"
                        "and our recorder's mode [{}]".format(
                            self.mode, self.record.mode))

    # Valid recording/playback states for the device
    self.states = []

    # A tune to record, playback or describe (if provided)
    self.tune = kwargs.get('tune', None)

    # Figure out which function describe_device() should delegate to in order
    # to describe this device.
    # Devices _may_ override describe_device() if they want but it is better
    # if they override describe_*_device().
    if self.mode == What.RECORD:
      self._describe_device = self.describe_recordable_device
      self._init_recordable(*args, **kwargs)
    elif self.mode in [What.PLAYBACK, What.DESCRIBE]:
      self._describe_device = self.describe_playable_device
      self._init_playable(*args, **kwargs)

    super().__init__()

  def __str__(self):
    return self.describe_device()

  def _init_recordable(self, *args, **kwargs):
    if not self.recorder:
      raise Exception("Recorder required in mode [{}].".format(self.mode))
    self.states.append('recording')
    self.timestamp = self.recorder.timestamp()

  def _init_playable(self, *args, **kwargs):
    pass

  def describe_device(self):
    logger.debug("Derived class [{}] missing describe_device(). Delegating to [{}].".format(
        self.__class__.__name__, self._describe_device))
    return self._describe_device()

  def describe_recordable_device(self):
    raise Exception("Derived class [{}] missing describe_recordable_device()".format(
        self.__class__.__name__))

  def describe_playable_device(self):
    raise Exception("Derived class [{}] missing describe_playable_device()".format(
        self.__class__.__name__))

  def record(self, tunes, when):
    '''Delegate to our Recorder.

      The Recorder acts as an intermediary between recordable Devices and
      the recording medium (i.e. - the Cassette). This is consistent with the
      Real World and also gives the Recorder an opportunity to modify the data
      (tunes) from the Device before committing them to tape if it wants.

      Args:
        tunes (dict): Stuff to record.
        when (When): When to record stuff.
    '''
    tunes.update({'when': when})
    self.recorder.record(device=self, tunes=tunes)
