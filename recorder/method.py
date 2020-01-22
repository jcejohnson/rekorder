
'''Decorators for recording repository state.
'''

from functools import wraps
import git

from . import repository
from .cassette import Cassette
from .exception_wrapper import ExceptionWrapper
from .when import When


def exception(func):
  '''A decorator that will record exceptions.
      The original exception is wrapped in ExceptionWrapper and rethrown.

      Usage:

        @exception
        some_func(...): ...
  '''

  f = func

  @wraps(f)
  def exception_wrapper(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except Exception as e:
      # TODO - Is this the best way to minimize our intrusion into the traceback?
      raise ExceptionWrapper(f, e, e.__traceback__, exception_recorder=exception) from e
  return exception_wrapper


def param(func=None, *, when=When.BEFORE):
  '''A decorator that will record method parameters.

      Usage:

        @param
        some_func(...): ...

        @param(decorator-parameters)
        some_func(...): ...

      :param enum when: When to record the parameter values (BEFORE, AFTER or AROUND)
  '''

  def param_wrapper(f):
    @wraps(f)
    def param_wrapper_inner(*args, **kwargs):
      if when in [When.BEFORE, When.AROUND]:
        _log(recorder=param, func=f, args=args, kwargs=kwargs)
      r = f(*args, **kwargs)
      if when in [When.AFTER, When.AROUND]:
        _log(recorder=param, func=f, args=args, kwargs=kwargs)
      return r
    return param_wrapper_inner

  if func:
    return param_wrapper(func)

  return param_wrapper


def rval(func):
  '''A decorator that will record the method return value.

      Usage:

        @rval
        some_func(...): ...
  '''

  f = func

  @wraps(f)
  def rval_wrapper(*args, **kwargs):
    r = f(*args, **kwargs)
    _log(recorder=rval, func=f, rval=r)
    return r
  return rval_wrapper


def everything(func=None, *, when=When.BEFORE):
  '''A decorator that will record the method return value, parameters and exceptions.

      Usage:

        @everything
        some_func(...): ...

        @everything(decorator-parameters)
        some_func(...): ...

      :param enum when: When to record the parameter values (BEFORE, AFTER or AROUND)

      Does _not_ capture repository state.
  '''

  def everything_wrapper(f):
    @param(when=when)
    @rval
    @exception
    @wraps(f)
    def everything_wrapper_inner(*args, **kwargs):
      return f(*args, **kwargs)
    return everything_wrapper_inner

  if func:
    return everything_wrapper(func)

  return everything_wrapper


def repository_state(func=None, *, paths=['.'], when=When.BEFORE):
  '''A decorator that will record the state of one or more repositories.

      Usage:

        @repository_state
        some_func(...): ...

        @repository_state(decorator-parameters)
        some_func(...): ...

      :param enum when: When to record the parameter values (BEFORE, AFTER or AROUND)
      :param list path: List of paths to repositories. Default is '.'
  '''

  def repository_state_wrapper(f):
    @wraps(f)
    def repository_state_inner_wrapper(*args, **kwargs):
      if when in [When.BEFORE, When.AROUND]:
        repository.repository_state(recorder=repository_state, func=f, paths=paths)
      r = f(*args, **kwargs)
      if when in [When.AFTER, When.AROUND]:
        repository.repository_state(recorder=repository_state, func=f, paths=paths)
      return r
    return repository_state_inner_wrapper

  if func:
    return repository_state_wrapper(func)

  return repository_state_wrapper


def _log(*args, **kwargs):
  '''Internal convenience function for Cassette.instance().record()
  '''
  Cassette.instance().record(*args, **kwargs)
