
from ..what import What
from ..when import When

from .decorator import Decorator


class MethodRepository(Decorator):
  '''Record the state of one or more repositories

      Can be invoked before, after or around method invocation.

      Args:
        when (When): Optional. Default is When.BEFORE.
        paths (list[str]): Optional. Default is ['.']

      Usage:

        @rekorder.method.repository  # Defaults to when=When.BEFORE
        def some_func(...):          # and paths=['.']

        @rekorder.method.repository(when=When.AROUND)
        def some_func(...):

        @rekorder.method.repository(paths=['some/path'])
        def some_func(...):
  '''

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    '''Construct a playback instance of `cls`.
    '''

    from ..repository import RepositoryManager

    obj = Decorator.playback_instance(cls, *args, **kwargs)
    obj.repository_manager = RepositoryManager.playback_instance(None, *args, **kwargs)

    return obj

  def validate(self, **kwargs):
    '''Override Device.validate() so that we can interact with the recording_medium.

        During playback validation, most Devices don't need to do anything different than
        what they do during recording. A MethodRepository Device, however, needs to restore
        the repository to its record-time state so that the wrapped method and downstream
        code will be working with the same repository content that was present when the
        recording was made. We do this in before() by fetching the recorded RepositoryState
        and replaying it. Because we have advanced the playback data we have to override
        validate() and provide the data we fetched in before(). If we don't do this, the
        default validate() method will read from the recording medium again which will
        be the _next_ Device's expectation.

        We could avoid this if Track had a way to peek at the next tune that will be returned
        by next_tune() without actually incrementing the internal iterator.
    '''

    if 'expectation' in kwargs:
      return super().validate(**kwargs)

    return super().validate(expectation=self.playback_expectation, **kwargs)

  def before(self, **moar):
    if self.mode == What.VALIDATE:
      self.playback_expectation = self.recorder.recording_medium.track_manager.current_track.next_tune()
      self.playback_expectation.device.repository_manager.repository_state.playback(rval=None)
    elif self.mode != What.RECORD:
      raise Exception("I don't know what to do in mode [{}].".format(self.mode))

    r = self.around(when=When.NA, paths=moar['paths'])
    return r

  def after(self, **moar):
    self.plaback_expectation = self.recorder.recording_medium.track_manager.current_track.next_tune()
    r = self.around(when=When.NA, paths=moar['paths'])
    return r

  def around(self, when, **moar):
    # repository_manager is a RepositoryManager instance
    # A new instance is returned on each call to recorder.repository_manager
    self.repository_manager = self.recorder.repository_manager

    states = self.repository_manager.get_notes(paths=moar['paths'])

    r = {
        **states,
        'function': {
            'name': self.function.__name__,
            'module': self.function.__module__
        }
    }
    return r

  def describe_device(self):
    m, n = self._describe_function()
    r = "{} {}.{} ... {}".format(
        self.__class__.__name__, m, n,
        self.repository_manager.describe_device()
    )
    return r

  def describe_recordable_device(self):
    return self.describe_device()

  def describe_playable_device(self):
    return self.describe_device()

  def __call__(self, function=None, *, when=When.BEFORE, paths=['.']):
    return super().__call__(function=function, when=when, paths=paths)

  def __eq__(self, other):
    return type(self) == type(other) and self.repository_manager == other.repository_manager
