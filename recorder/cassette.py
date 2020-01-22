
import json
import time


class Cassette:
  '''Record interesting events and write them to a file.
  '''

  _instance = None

  @classmethod
  def initialize(cls, path):
    '''Initialize the singleton's output file path.
    '''

    if cls._instance:
      raise Exception("Already initialized!")

    cls._instance = Cassette(path)

  @classmethod
  def instance(cls):
    return cls._instance

  def __init__(self, path):
    self._path = path
    self._events = []

  def record(self, recorder, func, **kwargs):
    '''Record an interesting event and save the event stream.
    '''
    blob = {
        'type': recorder.__name__,
        'func': func.__name__,
        'module': func.__module__,
        'time': time.time()
    }
    blob['localtime'] = time.asctime(time.localtime(blob['time']))
    self._record(blob, **kwargs)
    self._events.append(blob)
    self.write()

  def write(self):
    '''Write (save) the current event stream to the singleton's file.
    '''
    with open(self._path, 'w') as f:
      json.dump(self._events, f)

  def _record(self, blob, **kwargs):
    # TODO - Make this smarter.
    for key, value in kwargs.items():
      if isinstance(value, dict):
        blob[key] = value
      elif isinstance(value, list) or isinstance(value, set) or isinstance(value, tuple):
        blob[key] = list(value)
      elif isinstance(value, int) or isinstance(value, float):
        blob[key] = value
      else:
        blob[key] = str(value)
