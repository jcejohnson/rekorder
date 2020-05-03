
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

  def before(self):
    return self.silence()

  def around(self, when):
    return self.silence()

  def after(self):
    # Similar to the default behavior but without args & kwargs.
    r = super().after()
    del(r['function']['args'])
    del(r['function']['kwargs'])
    return r

  def __call__(self, function):
    # rval only has meaning after a function's invocation
    return super().__call__(function=function, when=When.AFTER)
