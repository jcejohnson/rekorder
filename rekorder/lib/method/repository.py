
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

  def before(self, **moar):
    return self.around(when=When.NA, paths=moar['paths'])

  def after(self, **moar):
    return self.around(when=When.NA, paths=moar['paths'])

  def around(self, when, **moar):
    # repository_manager is a RepositoryManager instance
    # A new instance is returned on each call to recorder.repository_manager
    self.repository_manager = self.recorder.repository_manager

    states = self.repository_manager.get_notes(paths=moar['paths'])

    return {
        **states,
        'function': {
            'name': self.function.__name__,
            'module': self.function.__module__
        }
    }

  def describe_device(self):
    m, n = self._describe_function()
    r = "{} {}.{} ... {}".format(
        self.__class__.__name__, m, n,
        self.repository_manager.describe_device()
    )
    return r

  def describe_recordable_device(self):
    return self.describe_device()

  def describe_recordable_device(self):
    return self.describe_device()

  def __call__(self, function=None, *, when=When.BEFORE, paths=['.']):
    return super().__call__(function=function, when=when, paths=paths)

  def __eq__(self, other):
    return type(self) == type(other) and self.repository_manager == other.repository_manager
