
class Recording:
  '''A Recording of tunes.

    This is data that has been previously recorded by a Device
    and can, presumably, be replayed.
  '''

  def __init__(self, recording):
    self._recording = recording

  def __getattr__(self, attr):
    return self._recording[attr]

  def __getitem__(self, attr):
    return self._recording[attr]
