
import os
import sys

from functools import wraps

from ..device import Device
from ..timestamp import Timestamp
from ..tune import Tune
from ..when import When


class Decorator(Device):
  '''Decorate a method so that we can record things about it.

    Decorator objects are callable and can be used with or without parameters.

    Usage:

      class MyDecorator(Decorator):
        ...

      d = MyDecorator()

      @d
      def some_func(...)

      @d(when=When.BEFORE)
      def some_other_func(...)

    Derived classes will typically override __init__() to provide a default
    value for `when` that makes sense for them.

    Derived classes should override one or more of before(), around(), after()
    to record the desired data at those points.

    Default behaviors:
      before  : Provides function module and name, args & kwargs
      after   : Provides function module and name, args & return value
      afround : Delegates to before(). If when is When.AFTER, delegates to
                after() and merges results.

    Advanced derivatives may want to override intro(), outtro(), invoke(),
    record() or the pre/post hooks around invoke() and record().
    See their definitions for more detail.

  '''

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    '''Construct a playback instance of `cls`.
    '''

    obj = Device.playback_instance(cls, *args, **kwargs)

    obj.timestamp = kwargs['timestamp']
    obj.when = When.map(kwargs['when'])

    # A Decorator's purpose is to record data about a function so, let's go
    # find the function we recorded.
    function = kwargs['function']

    module, name = function['module'], function['name']
    file = function.get('file', None)
    obj.function = function  # kwargs['player'].get_object(module, name, file=file)

    # These kind of make sense on the derived objects that care about them
    # but since it is Decorator's before() and after() methods that capture
    # them it makes _more_ sense to put them here.

    if 'args' in function:
      obj.args = tuple(function['args'])  # list -> tuple
    if 'kwargs' in function:
      obj.kwargs = function['kwargs']
    if 'rval' in function:
      obj.rval = function['rval']

    return obj

  def __init__(self, *args, when=When.AROUND, **kwargs):
    '''Construct the Decorator.

      Args:
        when (When): When this decorator will record: before, around or after
                     method invocation. Default is When.AROUND.
    '''

    super().__init__(*args, when=when, **kwargs)

  def _describe_function(self):
    if isinstance(self.function, dict):
      m = self.function['module']
      n = self.function['name']
    else:
      m = self.function.__module__
      n = self.function.__name__
    return m, n

  def intro(self, **moar):
    '''This is called immediately upon entering the function wrapper.
        Its output is not recorded.
    '''
    pass

  def before(self, **moar):
    '''Called before method invocation only if when=When.BEFORE.

        Method parameters are available as self.args and self.kwargs.

        Returns a dict representing the Notes of the Tune to be recorded.

        Default behavior:
          Provides function module and name, args & kwargs
    '''
    from ..recorder import Recorder
    return {
        'function': {
            'name': self.function.__name__,
            'qualname': self.function.__qualname__,
            'module': self._get_module_of(self.function),
            'args': self.args,
            'kwargs': self.kwargs,
        }
    }

  def around(self, when, **moar):
    '''Called both before and after method invocation only if
        when=When.AROUND.

        The `when` parameter can be useful if a derived class
        needs to do different things for before and after.

        Method parameters are available as self.args and self.kwargs.

        Method result is available as self.result after metthod invocation
        (it is undefined before method invocation).

        Returns a dict representing the Notes of the Tune to be recorded.

        Default behavior:
          Delegates to before() or after() based on value of `when`.
    '''
    if when == When.BEFORE:
      return self.before(**moar)
    if when == When.AFTER:
      return self.after(**moar)
    raise Exception("Illegal value for when : [{}]".format(when))

  def after(self, **moar):
    '''Called after method invocation only if when=When.AFTER.

        Method parameters are available as self.args and self.kwargs.
        Method result is available as self.result.

        Returns a dict representing the Notes of the Tune to be recorded.

        Default behavior:
          Provides function module and name, args, kwargs & result.
    '''
    return {
        'function': {
            'name': self.function.__name__,
            'qualname': self.function.__qualname__,
            'module': self._get_module_of(self.function),
            'args': self.args,
            'kwargs': self.kwargs,
            'rval': self.rval
        }
    }

  def _get_module_of(self, function):
    '''Get the module that owns the function we are recording.
    '''

    if self.function.__module__ == '__main__':
      return sys.modules[self.function.__module__].__file__.replace('/', '.').replace('.py', '')
    return function.__module__

  def outtro(self, **moar):
    '''This is called immediately before returning from function wrapper.
        Its output is not recorded.
    '''
    pass

  def pre_invoke(self):
    pass

  def invoke(self):
    '''Invoke the wrapped function.
    '''
    self.pre_invoke()
    rval = self.function(*self.args, **self.kwargs)
    # Note that other wrapped functions may be called by self.function()
    # before we find ourselves back here.
    rval = self.post_invoke(rval)
    return rval

  def post_invoke(self, rval):
    return rval

  def silence(self, *args, **kwargs):
    '''Utility method for derivatives that want to record silence for one or
        more of before(), around() or after() instead of the default notes.
    '''
    return {}

  def __call__(self, function=None, *, when=When.NA, **moar):

    self.when = when

    def wrapper(f):

      self.function = f

      def wrapper_inner(*args, **kwargs):

        self.args, self.kwargs, self.rval = args, kwargs, None

        self.intro(**moar)

        self._baa(when, When.BEFORE, self.before, **moar)

        self.rval = self.invoke()

        self._baa(when, When.AFTER, self.after, **moar)

        self.outtro(**moar)

        return self.rval

      return Decorator.wrap_if_necessary(self, self.function, wrapper_inner)

    if function:
      return wrapper(function)

    return wrapper

  def _baa(self, when, target, function, **moar):
    # Before/Around/After

    if when == target:
      notes = function(**moar)
    elif when == When.AROUND:
      notes = self.around(when=target, **moar)
    else:
      return

    # record the notes from the device when mode is RECORD
    # validate the notes from the device against the recorded notes when when mode is VALIDATE.
    self.record(notes=notes, when=target)

  # Device

  @staticmethod
  def wrap_if_necessary(decorator, function, wrapper):

    # Mark the wrapper so that we can tell if we are wrapping a wrapper.
    # This is important because on playback we need to know when to invoke
    # a decorated function and when not to.
    wrapper._is_a_Method_decorator = True

    if not decorator.recorder.debug:
      return wraps(function)(wrapper)

    # If the function we are wrapping has the _is_a_Method_decorator attribute
    # then it is a wrapper we previously created. In this case we do not want
    # to @wraps() it because it's function metadata may be useful in debugging.
    if hasattr(function, '_is_a_Method_decorator'):
      return wrapper

    # Apply @wraps() to functions that are not our wrappers.
    return wraps(function)(wrapper)
