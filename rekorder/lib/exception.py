
import sys
import traceback

from .cassette import Cassette
from .when import When


class RecorderException(Exception):
  '''Wrap an exception & record the event.
      This lets custom exception handler focus on the original exception.
  '''

  def __init__(self, recordable, original):
    self.original = original
    self.traceback = original.__traceback__
    recordable.record(
        when=When.EXCEPTION,
        tunes={
            'original': original.__class__.__name__,
            'traceback': traceback.format_tb(original.__traceback__)
        }
    )


def exception_handler(exception_type, exception, traceback):
  '''A custom exception handler that will ignore as much of the Recorder traceback as possible.
  '''
  if exception_type == RecorderException:
    exception_type = type(exception.original)
    traceback = exception.traceback
    exception = exception.original
    print("Got RecorderException!!")
  system_exception_handler(exception_type, exception, traceback)


system_exception_handler = sys.excepthook
sys.excepthook = exception_handler
