
from ..what import What
from ..when import When

from .decorator import Decorator


class MethodReturn(Decorator):
  '''Record a method's return value.

      Will only be called after method invocation.
      Method result is available as self.rval.

      Args:
        None

      Usage:

        @rekorder.method.rval
        def some_func(...):
  '''

  def __eq__(self, other):
    '''Compare the attributes common between describe_playable_device() and describe_recordable_device()
    '''
    if type(self) != type(other):
      return False
    if self.__class__ != other.__class__:
      return False
    if self.when != other.when:
      if When.AROUND not in [self.when, other.when]:
        return False
    if self._describe_function() != other._describe_function():
      return False
    if self.rval != other.rval:
      return False
    return True

  def describe_playable_device(self):
    return "{} {}.{}(...) [mock:{}] -> [{}]".format(
        self.__class__.__name__,
        self.function['module'],
        self.function['name'],
        self.function['mock'],
        self.function['rval']
    )

  def describe_recordable_device(self):
    return "{} {}.{}(...) [mock:{}] -> [{}]".format(
        self.__class__.__name__,
        self.function.__module__,
        self.function.__name__,
        self.mock,
        self.rval
    )

  def before(self):
    r = super().before()
    r['function']['mock'] = self.mock
    r['function']['rval'] = None
    # Remove args & kwargs that were provided by super().after()
    del(r['function']['args'])
    del(r['function']['kwargs'])
    return r

  def after(self):
    r = super().after()
    r['function']['mock'] = self.mock
    # Remove args & kwargs that were provided by super().after()
    del(r['function']['args'])
    del(r['function']['kwargs'])
    return r

  def around(self, when):

    if when == When.BEFORE:
      if self.mock:
        self.recorder.recording_medium.track_manager.sub_track_begin('mock')
      return self.before()

    if when == When.AFTER:
      if self.mock and self.mode == What.RECORD:
        self.recorder.recording_medium.track_manager.sub_track_conclude('mock')
      return self.after()

    raise Exception("Programmer error: when = {}".format(when))

  def invoke(self):

    if not (self.mode == What.VALIDATE and self.mock):
      return super().invoke()

    self.recorder.recording_medium.track_manager.sub_track_conclude('mock')
    self.playback_expectation = self.recorder.recording_medium.track_manager.current_track.next_tune()
    return self.playback_expectation.notes['function']['rval']

  def validate(self, when, **kwargs):

    if 'expectation' in kwargs:
      # Possibly recursion.
      # The only time kwargs should contain 'expectation' is when we call
      # super().validate() from this method.
      raise Exception("Programmer error.")

    if not self.mock:
      return super().validate(when=when, **kwargs)

    if when == When.AFTER:
      return super().validate(expectation=self.playback_expectation, when=when, **kwargs)

    return

  def __call__(self, function=None, mock=False, when=When.AROUND, **moar):
    self.mock = mock
    return super().__call__(function=function, when=when)
