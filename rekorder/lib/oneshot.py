
from functools import wraps


class OneShot:
  '''Ensure that a given method is only ever invoked once.
  '''

  def __init__(self, function):
    self.function = function
    self.instance = None

  def __call__(self, *args, **kwargs):

    if 'reset_oneshot' in kwargs and kwargs['reset_oneshot']:
      del(kwargs['reset_oneshot'])
    else:
      if hasattr(self.instance, str(repr(self))):
        raise Exception("{}.{} has already been used.".format(
            repr(self.instance), self.function))

    setattr(self.instance, str(repr(self)), True)

    self.args, self.kwargs = args, kwargs
    self.rval = self.function(*self.args, **self.kwargs)

    return self.rval

  def __get__(self, instance, owner):
    self.instance = instance
    from functools import partial
    return partial(self.__call__, self.instance)
