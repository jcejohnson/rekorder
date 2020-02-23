
import os
import sys

from functools import wraps

from ..device import Device
from ..timestamp import Timestamp
from ..tune import Tune
from ..when import When


class Decorator(Device):
  '''Decorate a method so that we can record things about it.

    Decorator objects are callable and can be used with our wihtout parameters.

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

    Advanced derivatives may want to override intro(), outtro(), invoke() or
    record(). See their definitions for more detail.

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
      obj.args = function['args']
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

  def intro(self, **moar):
    '''This is called immediately upon entering the function wrapper.
        Its output is not recorded.
    '''
    pass

  def before(self, **moar):
    '''Called before method invocation only if when=When.BEFORE.

        Method parameters are available as self.args and self.kwargs.

        Returns the tune to be recorded.

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

        Returns the tune to be recorded.

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

        Returns the tune to be recorded.

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

  def pre_record(self, tune):
    pass

  def record(self, tune):
    '''Delegate to our Recorder.

      The Recorder acts as an intermediary between ourself and the recording
      medium (i.e. - the Cassette). This is consistent with the Real World and
      also gives the Recorder an opportunity to modify the data (tunes) we
      provide before committing them to tape if it wants.
    '''
    if not tune:
      return
    self.pre_record(tune=tune)
    self.recorder.record(tune=tune)
    self.post_record(tune=tune)

  def post_record(self, tune):
    pass

  def silence(self, *args, **kwargs):
    '''Utility method for derivatives that want to record silence for one or
        more of before(), around() or after() instead of the default tune.
    '''
    return {}

  def __call__(self, function=None, *, when=When.NA, **moar):

    if 'func' in moar:
      raise Exception("oops")

    def wrapper(f):

      self.function = f

      def wrapper_inner(*args, **kwargs):

        # if not hasattr(self.function, '_is_a_Method_decorator'):
        #   print("Begin new track for [{}]".format(self.function))

        self.intro(**moar)

        self.args = args
        self.kwargs = kwargs

        if when == When.BEFORE:
          tune = Tune(device=self, notes=self.before(**moar), when=When.BEFORE)
        elif when == When.AROUND:
          tune = Tune(device=self, notes=self.around(when=When.BEFORE, **moar), when=When.BEFORE)
        else:
          tune = None

        self.record(tune=tune)

        self.rval = self.invoke()
        # Note that self.result will be undefined if self.invoke() throws an exception.

        if when == When.AFTER:
          tune = Tune(device=self, notes=self.after(**moar), when=When.BEFORE)
        elif when == When.AROUND:
          tune = Tune(device=self, notes=self.around(when=When.AFTER, **moar), when=When.AFTER)
        else:
          tune = None

        self.record(tune=tune)

        self.outtro(**moar)

        # if not hasattr(self.function, '_is_a_Method_decorator'):
        #   print("End track for [{}]".format(self.function))

        return self.rval

      return Decorator.wrap_if_necessary(self, self.function, wrapper_inner)

    if function:
      return wrapper(function)

    return wrapper

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
