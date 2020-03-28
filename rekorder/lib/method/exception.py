
import traceback

from .decorator import Decorator

from ..device import Device
from ..when import When


class MethodException(Device):
  '''Record exceptions thrown by methods.

    MethodException does not extend Decorator because it needs a custom
    __call__() method which is kind of the whole point of Decorator.
  '''

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    obj = Device.playback_instance(cls, *args, **kwargs)
    obj.cls = kwargs['class']
    obj.message = kwargs['message']
    obj.traceback = kwargs['traceback']
    return obj

  def _init_playable(self, *args, **kwargs):
    '''kwargs is our recorded tune's notes.
        See exception_wrapper()
    '''
    self.cls = kwargs['class']
    self.message = kwargs['message']
    self.traceback = kwargs['traceback']

  def describe_device(self):
    r = "{} [{}] [{}] [{}]".format(
        self.__class__.__name__,
        self.cls,
        self.message,
        self.traceback[-1].replace('\n', '<nl>')
    )
    return r

  def describe_playable_device(self):
    return self.describe_device()

  def describe_recordable_device(self):
    return self.describe_device()

  def __call__(self, function):
    '''A decorator that will record exceptions.
        The original exception is wrapped in ExceptionWrapper and rethrown.

      Args:
        function (function): Function to record the exceptions of.

      Usage:

        @rekorder.method.exception
        some_func(...): ...
    '''

    self.function = function

    def exception_wrapper(*args, **kwargs):
      try:
        return function(*args, **kwargs)
      except Exception as original:
        self.cls = original.__class__.__name__
        self.message = str(original)
        self.traceback = traceback.format_tb(original.__traceback__)
        self.record(
            when=When.EXCEPTION,
            notes={
                'class': self.cls,
                'message': self.message,
                'traceback': self.traceback
            }
        )
        raise

    return Decorator.wrap_if_necessary(self, self.function, exception_wrapper)

  def __eq__(self, other):
    return type(self) == type(other) and self.cls == other.cls and self.message == other.message
