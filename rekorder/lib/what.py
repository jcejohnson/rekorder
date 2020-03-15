
from enum import Enum


class What(Enum):
  '''What are we doing?

    Tell something that we want it to record, playback, describe or verify itself.
  '''
  RECORD = 201
  PLAYBACK = 202
  DESCRIBE = 203
  VALIDATE = 204
