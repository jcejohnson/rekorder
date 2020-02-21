
import copy

from functools import wraps

from .cassette import Cassette
from .device import Device
from .manager import RecordableDeviceManager
from .method import Method
from .method import MethodParameters
from .method import MethodReturn
from .repository import Repository
from .timestamp import Timestamp
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

  @staticmethod
  def playback_instance(cls, mode, tune, *args, **kwargs):
    return Recorder(mode=mode, **tune['data'])

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
      self.states.append('header')

      self.cassette = Cassette(*args, timestamp=self.timestamp(), recorder=self, **kwargs)
      self.record(device=self, tunes={'name': self.name})

    elif self.mode == What.DESCRIBE:
      pass

    elif self.mode == What.PLAYBACK:
      # A Player must be provided in Playback mode.
      self.player = kwargs['player']

    else:
      raise Exception("Unknown mode [{}]".format(self.mode))

    # Add ourselves to the dict of named recorders
    Recorder.__save_recorder(self)

  def record(self, device, tunes):
    '''Record some tunes on a cassette for later playback.

      This method is typically used by Devices when they wan to
      record something interesting on the Recorder's Cassette instance.
      It _can_ be used directly but that is discouraged.

      Args:
        device (Device): A recordable Device capable of producing tunes.
        tunes (dict): A dict of interesting information (tunes) to be recorded.
    '''
    self.cassette.record(device=device, tunes=tunes, timestamp=self.timestamp())

  # Manage the recording lifecycle

  def begin_recording(self):
    self.cassette.begin_recording()

  def end_recording(self):
    self.cassette.end_recording()

  def timestamp(self):
    return Timestamp()

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


class RecordingBegin(MethodParameters):
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

  # MethodParameters

  def intro(self, **moar):
    '''This is called immediately upon entering the function wrapper.
        Its return value is not recorded.
    '''
    self.recorder.begin_recording()

  def __call__(self, function):
    # Only allow When.BEFORE. Do not allow parameters.
    return super().__call__(function=function, when=When.BEFORE)


class RecordingEnd(MethodReturn):
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

  # MethodReturn

  def outtro(self, **moar):
    '''This is called immediately before returning from function wrapper.
        Its return value is not recorded.
    '''
    self.recorder.end_recording()
