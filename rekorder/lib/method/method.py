
from ..device import DeviceManager
from ..what import What
from ..when import When

from .decorator import Decorator
from .exception import MethodException
from .parameters import MethodParameters
from .repository import MethodRepository
from .rval import MethodReturn


class Method(DeviceManager):
  '''Record interesting things about methods.

    Usage:

      @rekorder.method.param(when=When.AROUND)
      @rekorder.method.rval
      @rekorder.method.exception
      @rekorder.method.repository(paths=['some/path'])
      def  some_func(...)

    Alternate Usage:

      Method can also be used as a decorator.
      This usage delegates to the param, rval and exception Devices.
      You must still use @rekorder.method.repository to record repository
      information.

        @rekorder(when=When.AROUND)
        def  some_func(...)
  '''

  def __init__(self, recorder):
    '''Construct the Method with a reference to the Recorder capable of
        recording the tunes created by our Recordable devices.

      Args:
        recorder (Recorder): Recorder instance.
    '''
    super().__init__()

    self.recorder = recorder
    self.params = MethodParameters(recorder=recorder)
    self.rval = MethodReturn(recorder=recorder)
    self.exception = MethodException(recorder=recorder)
    self.repository = MethodRepository(recorder=recorder)
    self.pass_recorder = MethodPassRecorder(recorder=recorder)

  def xxxpass_recorder(self, function):
    '''Use this decorator to pass the Recorder instance to a method that is
        being recorded.
    '''

    function._playback_requires_recorder = True

    def wrapper(*args, **kwargs):
      return function(self.recorder, *args, **kwargs)

    return Decorator.wrap_if_necessary(self, function, wrapper)

  #

  def __call__(self, function=None, *, when=When.AROUND, **kwargs):
    '''Delegate to some of our Devices in a reasonable order.
    '''
    function = self.exception(function=function, **kwargs)
    function = self.rval(function=function, **kwargs)
    function = self.param(function=function, when=when, **kwargs)
    return function


class MethodPassRecorder(MethodParameters):

  # Decorator

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    obj = MethodParameters.playback_instance(cls, *args, **kwargs)
    if obj.mode == What.DESCRIBE:
      obj.args = tuple(['<Recorder>'] + list(obj.args))
    return obj

  def invoke(self):
    '''Invoke the wrapped function.
    '''
    return self.function(self.recorder, *self.args, **self.kwargs)

  def __call__(self, function):
    return super().__call__(function=function, when=When.BEFORE)
