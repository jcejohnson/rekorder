
class SimpleState:

  def __init__(self, *args, states=[], **kwargs):
    if not states:
      raise Exception("Missing or empty `states` parameter.")
    self._states = states
    self.reset()

  @property
  def current(self):
    return self.states[self._index]

  @property
  def states(self):
    return self._states

  def next(self):
    self._index += 1
    if self._index > len(self._states):
      raise Exception("Attempt to increase state beyond maximum.")

  def reset(self):
    self._index = 0
