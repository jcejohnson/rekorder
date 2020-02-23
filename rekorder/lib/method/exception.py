
import traceback

from .decorator import Decorator

from ..device import Device
from ..when import When


class MethodException(Device):
  '''Record exceptions thrown by methods.

    MethodException does not extend Decorator because it needs a custom
    __call__() method which is kind of the whole point of Decorator.
  '''

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def _init_playable(self, *args, **kwargs):
    self.original = kwargs['original']
    self.traceback = kwargs['traceback']

  def describe_playable_device(self):
    r = "{} [{}] [{}]".format(
        self.__class__.__name__,
        self.original,
        self.traceback[-1].replace('\n', '<nl>')
    )
    return r

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
        self.record(
            when=When.EXCEPTION,
            tunes={
                'original': original.__class__.__name__,
                'traceback': traceback.format_tb(original.__traceback__)
            }
        )
        raise

    return Decorator.wrap_if_necessary(self, self.function, exception_wrapper)
