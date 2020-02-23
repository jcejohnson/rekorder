
import copy

from functools import wraps

from .cassette import Cassette
from .device import Device
from .manager import RecordableDeviceManager
from .method import Method
from .method import MethodParameters
from .method import MethodReturn
from .repository import Repository
from .tune import Tune
from .what import What
from .when import When


class Recorder(RecordableDeviceManager, Device):
  '''A Recorder is the central object.

    It gives us the means of recording and replaying simple CLI apps.

    All Recordable devices are given a reference to us (a Recorder) and we
    delegate to our Cassette to do the actual recording.

    This aproach lets the Recorder stand as an intermediary between Recordable
    devices and the recording medium (Cassette) thus allowing the Recorder to
    modify the data (tunes) before committing them to the Cassette.

    By giving each Recordable device a reference to the Recorder, it gives
    them the opportunity to interact through the recorder (e.g. - so that
    MethodRepository can leverage Repository.get_states())

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
    if 'mode' not in kwargs:
      kwargs = copy.copy(kwargs)
      kwargs['mode'] = What.RECORD

    self.debug = False

    super().__init__(*args, recorder=self, **kwargs)

    self.name = kwargs['name']

    if self.mode == What.RECORD:  # Record mode

      self.cassette = Cassette(*args, recorder=self, **kwargs)
      self.record(tune=Tune(device=self, notes={'name': self.name}))

    elif self.mode == What.DESCRIBE:
      pass

    elif self.mode == What.PLAYBACK:
      # A Player must be provided in Playback mode.
      self.player = kwargs['player']

    else:
      raise Exception("Unknown mode [{}]".format(self.mode))

    # Add ourselves to the dict of named recorders
    Recorder.__save_recorder(self)

  def record(self, tune):
    '''Record a tune on a cassette for later playback.

        Delegates to our cassette so that the recording medium is not exposed
        directly to the devices.

        This method is typically used by Devices when they want to
        record something interesting on the Recorder's Cassette instance.
        It _can_ be used directly but that is discouraged.
    '''

    self.cassette.record(tune=tune)

  # Manage the recording lifecycle

  def next_track(self):
    '''Move to the next track on the recording medium.

        Delegates to our cassette so that the recording medium is not exposed
        directly to the devices.
    '''
    self.cassette.next_track()

  # When used as a callable object

  def __call__(self, function=None, *, when=When.AROUND, **kwargs):
    '''Invoked when Recorder is used as a decorator.

      Usage:
        recorder = Recorder.get_recorder(...)

        @rekorder  # Implicitly uses the RecordingBegin and RecordingEnd decorators.
        def some_function(...)
    '''

    # This arrangement replicates:
    #    @rekorder.begin
    #    @rekorder.end
    #    def some_function(...)
    function = self.end(function=function, **kwargs)
    function = self.begin(function=function, **kwargs)
    return function

  #

  @property
  def begin(self):
    '''Invoked when Recorder delegates to the RecordingBegin decorator.

      Usage:
        recorder = Recorder.get_recorder(...)

        @rekorder.begin
        def some_function(...)
    '''
    return RecordingBegin(recorder=self)

  @property
  def end(self):
    '''Invoked when Recorder delegates to the RecordingEnd decorator.

      Usage:
        recorder = Recorder.get_recorder(...)

        @rekorder.end
        def some_function(...)
    '''
    return RecordingEnd(recorder=self)

  # Other RecordableDeviceManager instances to which we delegate.

  @property
  def method(self):
    '''This property has decorators to record method parameters, return values
        and exceptions.
    '''
    return Method(recorder=self)

  @property
  def repository_state(self):
    '''This property's state() decorator will let you record the state of one
        or more repositories before and/or after method invocation.
    '''
    return Repository(recorder=self)

  # Device

  def describe_device(self):
    return "{} name=[{}] mode=[{}]".format(
        self.__class__.__name__, self.name, self.mode)

  def recordable(self, track_title):
    '''A Recorder can only record its information to the header track.
    '''
    return track_title == 'header'


class RecordingManager:

  # Decorator

  def pre_record(self, *args, **kwargs):
    '''Before our tunes have been recorded, tell the Recorder to move to the
        next track. This will put our data into the 'entry' track.
    '''
    self.recorder.next_track()

  def post_record(self, *args, **kwargs):
    '''Before our tunes have been recorded, tell the Recorder to move to the
        next track. This will put our data into the 'recording' track.
        We have to do this here because the wrapped function may invoke other
        wrapped functions and we need to be sure that their tunes are on the
        'recording' track.
    '''
    self.recorder.next_track()


class RecordingBegin(RecordingManager, MethodParameters):
  '''Declare the beginning of a recording.

      Every recording must have one of these.
      Anything recorded prior to this is considered configuration / setup.

      Always invoked before method invocation.

      Args:
        None

      Usage:

        @rekorder.before
        def some_func(...):
  '''

  # Device

  def describe_device(self):
    return super().describe_device() + " @ [{}]".format(self.timestamp.localtime)

  def recordable(self, track_title):
    '''RecordingBegin can only record its information to the header track.
    '''
    return track_title == 'entry'

  def __call__(self, function):
    # Only allow When.BEFORE. Do not allow parameters.
    return super().__call__(function=function, when=When.BEFORE)


class RecordingEnd(RecordingManager, MethodReturn):
  '''Declare the end of a recording.

      This is optional.
      If an exception is thrown it won't be called.

      Always invoked after method invocation.

      Args:
        None

      Usage:

        @rekorder.end
        def some_func(...):
  '''

  # Device

  def describe_device(self):
    return super().describe_device() + " @ [{}]".format(self.timestamp.localtime)

  def recordable(self, track_title):
    '''RecordingBegin can only record its information to the header track.
    '''
    return track_title == 'exit'
