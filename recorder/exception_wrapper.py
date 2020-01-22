
import sys

from .cassette import Cassette


class RecorderExceptionWrapper(Exception):
  '''Wrap an exception & record the event.
      This lets custom exception handler focus on the original exception.
  '''

  def __init__(self, func, original, traceback, *args, exception_recorder, **kwargs):
    Cassette.instance().record(recorder=exception_recorder, func=func,
                               module=func.__module__,
                               clazz=original.__class__.__name__,
                               message=original,
                               )
    self.func = func
    self.original = original
    self.traceback = traceback


def exception_handler(exception_type, exception, traceback):
  '''A custom exception handler that will ignore as much of the Recorder traceback as possible.
  '''
  if exception_type == RecorderExceptionWrapper:
    exception_type = type(exception.original)
    traceback = exception.traceback
    exception = exception.original
  system_exception_handler(exception_type, exception, traceback)


system_exception_handler = sys.excepthook
sys.excepthook = exception_handler
