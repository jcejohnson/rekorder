
from ..when import When

from .decorator import Decorator


class MethodRepository(Decorator):
  '''Record the state of one or more repositories

      Can be invoked before, after or around method invocation.

      Args:
        when (When): Optional. Default is When.BEFORE.
        paths (list[str]): Optional. Default is ['.']

      Usage:

        @rekorder.method.repository_state  # Defaults to when=When.BEFORE
        def some_func(...):                # and paths=['.']

        @rekorder.method.repository_state(when=When.AROUND)
        def some_func(...):

        @rekorder.method.repository_state(paths=['some/path'])
        def some_func(...):
  '''

  def before(self, paths, **ignored):
    return self.around(when=When.NA, paths=paths)

  def after(self, paths, **ignored):
    return self.around(when=When.NA, paths=paths)

  def around(self, when, paths, **ignored):
    states = self.recorder.repository_state.get_states(paths=paths)
    return {
        'repositories': states,
        'function': {
            'name': self.function.__name__,
            'module': self.function.__module__
        }
    }

  def __call__(self, function=None, *, when=When.BEFORE, paths=['.']):
    return super().__call__(function=function, when=when, paths=paths)
