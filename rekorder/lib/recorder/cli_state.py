
import sys

from ..device import Device
from ..when import When


class CliState(Device):

  def _init_recordable(self, *args, **kwargs):
    self.sys_argv = sys.argv

  def _init_playable(self, *args, **kwargs):
    '''kwargs is our recorded tune's notes.
        See record()
    '''
    self.sys_argv = kwargs['argv']

  def describe_playable_device(self):
    r = "{} {}".format(
        self.__class__.__name__,
        ' '.join(["[{}]".format(arg) for arg in self.sys_argv])
    )
    return r

  def describe_recordable_device(self):
    r = "{} {}".format(
        self.__class__.__name__,
        ' '.join(["[{}]".format(arg) for arg in sys.argv])
    )
    return r

  def playback(self, *args, rval, **kwargs):
    sys.argv = self.sys_argv
    return rval

  def record(self):
    super().record(notes={'argv': sys.argv}, when=When.NA)

  def recordable(self, track_title):
    return track_title == 'header'
