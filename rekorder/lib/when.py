
from enum import Enum


class When(Enum):
  '''When should recording take place.

      Some Method recorders have the option of recording before or after
      method invocation. Or both before and after.
  '''
  NA = 100
  BEFORE = 101
  AFTER = 102
  AROUND = 103
  EXCEPTION = 110

  @staticmethod
  def map(string):
    if string.startswith(When.__name__):
      return When[string.replace(When.__name__, '')[1:]]
    raise Exception("Cannot convert [{}] to When.".format(string))

  @staticmethod
  def recordable_data(obj):
    return str(obj)
