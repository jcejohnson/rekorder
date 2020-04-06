
import logging

from ..tune import Tune
from ..what import What
from ..when import When

logger = logging.getLogger(__name__)


class Device:
  '''A thing that can be recorded, played back or described.
  '''

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    return cls(*args, **kwargs)

  def __init__(self, *args, **kwargs):

    if not kwargs.get('mode', None) and not kwargs.get('recorder', None):
      raise Exception("Programmer error. kwargs missing both node and recorder.")

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

    # Most devices will wrap function calls so we treat 'when' as a core attribute.
    self.when = kwargs.get('when', When.NA)

    # Figure out which function describe_device() should delegate to in order
    # to describe this device.
    # Devices _may_ override describe_device() if they want but it is better
    # if they override describe_*_device().
    if self.mode == What.RECORD:
      self._describe_device = self.describe_recordable_device
      self._init_recordable(*args, **kwargs)
    elif self.mode == What.VALIDATE:
      self._describe_device = self.describe_recordable_device
      self._init_for_validate(*args, **kwargs)
    elif self.mode == What.DESCRIBE:
      self._describe_device = self.describe_playable_device
      self._init_describable(*args, **kwargs)
    elif self.mode == What.PLAYBACK:
      self._describe_device = self.describe_playable_device
      self._init_playable(*args, **kwargs)

    super().__init__()

  def __str__(self):
    return self.describe_device()

  def __eq__(self, other):
    raise Exception("Derived class [{}] missing __eq__()".format(
        self.__class__.__name__))

  def _init_recordable(self, *args, **kwargs):
    if not self.recorder:
      raise Exception("Recorder required in mode [{}].".format(self.mode))

  def _init_for_validate(self, *args, **kwargs):
    self._init_recordable(*args, **kwargs)
    self.__record__, self.record = self.record, self.__validate__

  def _init_describable(self, *args, **kwargs):
    pass

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

  def record(self, notes, when):
    '''Delegate to our Recorder.

      The Recorder acts as an intermediary between recordable Devices and
      the recording medium (i.e. - the Cassette). This is consistent with the
      Real World and also gives the Recorder an opportunity to modify the data
      (notes) from the Device before committing them to tape if it wants.

      A derived class may choose to override this method and internally provide
      the notes. For instance:

        class MyDevice(Device):
          def record(self, message):
            super().record(notes={'message': 'Hello World'})

        MyDevice(recorder=Recorder.get_recorder(...)).record()

      Args:
        notes (dict): Stuff to record.
        when (When): When stuff is recorded.
    '''
    tune = Tune(device=self, notes=notes, when=when)
    self.recorder.record(tune=tune)

  def validate(self, notes, when, **kwargs):
    '''Validate playback activity against recorded state.
    '''

    # Fetch the data from the recording_medium by reading the next tune.
    expectation = kwargs['expectation'] \
        if 'expectation' in kwargs else self.recorder.recording_medium.track_manager.current_track.next_tune()

    # Compare tune to what was just recorded.
    actual = self.recorder.recording_medium.last_tune

    from ..method import MethodRepository

    if actual.device != expectation.device:
      self.validation_failure(actual, expectation)

  def validation_failure(self, actual, expectation):
    raise Exception("Device expectation failed: expectation [{}] actual [{}]".format(
        expectation.device, actual.device))

  def recordable(self, track_title):
    '''Is this device recordable for the named track?
        Almost all devices are recordable in he 'recording' track, so that's
        our default.
    '''
    return track_title == 'recording'

  def __validate__(self, *args, notes, when, **kwargs):
    '''Replaces record() in VALIDATE mode.
        Delegates to the original record() method then to validate().
        The idea is to transparently invoke validate() after record().
    '''
    self.__record__(*args, notes=notes, when=when, **kwargs)
    self.validate(*args, notes=notes, when=when, **kwargs)
