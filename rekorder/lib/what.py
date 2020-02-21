
from enum import Enum


class What(Enum):
  '''What are we doing?

    Tell something that we want it to record, playback or describe itself.
  '''
  RECORD = 201
  PLAYBACK = 202
  DESCRIBE = 203

  # @classmethod
  # def map(cls, what):
  #   if what in [cls.RECORD]:
  #     return cls.RECORD
  #   if what in [cls.PLAYBACK]:
  #     return cls.PLAYBACK
  #   if what in [cls.DESCRIBE]:
  #     return cls.DESCRIBE
  #   raise Exception("Illegal Record mode [{}]".format(what))
