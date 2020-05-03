
from ..what import What
from ..when import When

from .decorator import Decorator


class MethodMock(Decorator):
  '''Mock a method call on playback.

      Args:
        None

      Usage:

        @rekorder.method.mock
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
    return "{} {}.{}(...) -> [{}]".format(
        self.__class__.__name__,
        self.function['module'],
        self.function['name'],
        self.function['rval']
    )

  def describe_recordable_device(self):
    return "{} {}.{}(...) -> [{}]".format(
        self.__class__.__name__,
        self.function.__module__,
        self.function.__name__,
        self.rval
    )

  def disabled_before(self):
    r = super().before()
    r['function']['rval'] = None
    # Remove args & kwargs that were provided by super().after()
    del(r['function']['args'])
    del(r['function']['kwargs'])
    return r

  def disabled_after(self):
    r = super().after()
    # Remove args & kwargs that were provided by super().after()
    del(r['function']['args'])
    del(r['function']['kwargs'])
    return r

  def around(self, when):

    if when == When.BEFORE:
      self.recorder.recording_medium.track_manager.sub_track_begin('mock')
      return self.before()

    if when == When.AFTER:
      if self.mode == What.RECORD:
        self.recorder.recording_medium.track_manager.sub_track_conclude('mock')
      return self.after()

    raise Exception("Programmer error: when = {}".format(when))

  def invoke(self):

    if self.mode != What.VALIDATE:
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

    if when == When.AFTER:
      return super().validate(expectation=self.playback_expectation, when=when, **kwargs)

    return

  def __call__(self, function=None, when=When.AROUND, **moar):
    return super().__call__(function=function, when=when)
