
import copy
import sys

from .cli_state import CliState
from .device import RecordingDevice
from .manager import RecordingManager

from ..cassette import Cassette
from ..device import DeviceManager
from ..method import Method
from ..repository import RepositoryManager
from ..tune import Tune
from ..what import What
from ..when import When


class Recorder(DeviceManager):
  '''A Recorder is the central object.

    It gives us the means of recording and replaying simple CLI apps.

    All Recordable devices are given a reference to us (a Recorder) and we
    delegate to our Cassette to do the actual recording.

    This aproach lets the Recorder stand as an intermediary between Recordable
    devices and the recording medium (Cassette) thus allowing the Recorder to
    modify the data (tunes) before committing them to the Cassette.

    By giving each Recordable device a reference to the Recorder, it gives
    them the opportunity to interact through the recorder (e.g. - so that
    MethodRepository can leverage RepositoryManager.get_states())

    Usage:

      Create a Recorder instance:

      rekorder = Recorder.get_recorder("my_recorder", output="path/to/output.json")

      As a decorator for methods:

      @rekorder.begin
      @rekorder.end
      @rekorder.method...
      @rekorder.method...
      def  some_func(...)

      As a tradutional function call:

      rekorder.repository_state.record(...)

    Alternate Usage:

      Recorder can also be used as a decorator.
      This usage is equivalent to the decorator example above:

        @rekorder  # Delegates to rekorder.begin & rekorder.end
        @rekorder.method...
        @rekorder.method...
        def  some_func(...)
  '''

  __recorders = {}

  @staticmethod
  def get_recorder(*args, name, **kwargs):
    '''Recorder instance factory.

      Args:
        name (str): Name of the Recorder. Will create new if necessary.
        mode (What): rekorder.What.RECORD (default) or rekorder.What.PLAYBACK.
        *args / **kwargs: Passed to Cassette() along with `mode`.
    '''
    if name not in Recorder.__recorders:
      Recorder(*args, name=name, **kwargs)
    return Recorder.__recorders[name]

  @staticmethod
  def __save_recorder(recorder):
    Recorder.__recorders[recorder.name] = recorder

  def __init__(self, *args, **kwargs):
    '''Construct the Recorder.

      Args:
        name (str): Name of the Recorder. Will create new if necessary.
        mode (What): rekorder.What.RECORD (default) or rekorder.What.PLAYBACK.
        *args / **kwargs: Passed to Cassette() along with `mode`.
    '''
    super().__init__()

    self.debug = False

    self.mode = kwargs.get('mode', What.RECORD)
    self.name = kwargs['name']

    if self.mode == What.RECORD:  # Record mode

      self.recording_medium = Cassette(*args, recorder=self, **kwargs)

      # When recording our data, use a RecordingDevice so that Recorder does
      # not need to be a Device. Things get too complicated if Recorder is
      # trying to play too many roles.
      RecordingDevice(recorder=self).record()
      # self.record(
      #     tune=Tune(
      #         device=RecordingDevice(recorder=self),
      #         notes={'name': self.name}
      #     )
      # )

      CliState(recorder=self).record()

    elif self.mode == What.DESCRIBE:
      pass

    elif self.mode == What.PLAYBACK:
      pass

    elif self.mode == What.VALIDATE:
      # Recorder should be created in RECORD, DESCRIBE or PLAYBACK mode.
      # The Player will change the Recorder's mode to VALIDATE at the appropriate time.
      raise Exception("Recorder should not be created in [{}] mode.".format(self.mode))

    else:
      raise Exception("Unknown mode [{}]".format(self.mode))

    self.recording_manager = RecordingManager(recorder=self)

    # Add ourselves to the dict of named recorders
    Recorder.__save_recorder(self)

  def record(self, tune):
    '''Record a tune on a recording_medium for later playback.

        Delegates to our recording_medium so that the recording medium is not exposed
        directly to the devices.

        This method is typically used by Devices when they want to
        record something interesting on the Recorder's Cassette instance.
        It _can_ be used directly but that is discouraged.
    '''

    self.recording_medium.record(tune=tune)

  # When used as a callable object

  def __call__(self, *args, **kwargs):
    '''Invoked when Recorder is used as a decorator.

      Usage:
        recorder = Recorder.get_recorder(...)

        @rekorder  # Implicitly uses the RecordingBegin and RecordingEnd decorators.
        def some_function(...)
    '''
    return self.recording_manager(*args, **kwargs)

  # Other Device instances to which we delegate.

  @property
  def begin(self):
    '''
        A new RecordingBegin is created on each call to begin.
    '''
    return self.recording_manager.begin

  @property
  def end(self):
    '''
        A new RecordingEnd is created on each call to end.
    '''
    return self.recording_manager.end

  @property
  def method(self):
    '''This property has decorators to record method parameters, return values
        and exceptions.

        A new Method is created on each call to repository_manager.
    '''
    return Method(recorder=self)

  @property
  def repository_manager(self):
    '''This property's state() decorator will let you record the state of one
        or more repositories before and/or after method invocation.

        A new RepositoryManager is created on each call to repository_manager.
    '''
    return RepositoryManager(recorder=self)
