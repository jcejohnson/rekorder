
import itertools

from ..when import When

from .decorator import Decorator


class MethodParameters(Decorator):
  '''Records method parameters.

      Can be invoked before, after or around method invocation.
      Default is When.BEFORE

      Args:
        when (When):

      Usage:

        @rekorder.method.param  # Defaults to when=When.BEFORE
        def some_func(...):

        @rekorder.method.param(when=When.AROUND)
        def some_func(...):
  '''

  # Device

  def describe_playable_device(self):
    r = "{} {}.{}({})".format(
        self.__class__.__name__,
        self.function['module'],
        self.function['name'],
        ', '.join(
            itertools.chain(
                [str(i) for i in self.args],
                [self._quote(k, v) for k, v in self.kwargs.items()]
            )
        )
    )
    if self.when != When.BEFORE:
      r = r + " [{}]".format(self.when)
    return r

  def describe_recordable_device(self):
    return "{} {}.{}({})".format(
        self.__class__.__name__,
        self.function.__module__,
        self.function.__name__,
        ', '.join(
            itertools.chain(
                [str(i) for i in self.args],
                [self._quote(k, v) for k, v in self.kwargs.items()]
            )
        )
    )

  def _quote(self, key, value):
    if not isinstance(value, str):
      return str(value)
    if not "'" in value:
      return "{}='{}'".format(key, value)
    if not '"' in value:
      return '{}="{}"'.format(key, value)
    return "{}='{}'".format(key, str(value).replace("'", "\\'"))

  # Decorator

  def before(self):
    # Default behavior is what we want
    return super().before()

  def around(self, when):
    return self.before()

  def after(self):
    return self.before()

  def __call__(self, function=None, *, when=When.BEFORE):
    # Default to When.BEFORE (Decorator defaults to When.AROUND)
    return super().__call__(function=function, when=when)
