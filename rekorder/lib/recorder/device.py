
from ..device import Device
from ..when import When


class RecordingDevice(Device):
  '''This is a wrapper of sorts so that we can record the Recorder details
      without forcing Recorder itself to be a Device.
  '''
  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    from . import Recorder
    return RecordingDevice(recorder=Recorder.get_recorder(*args, **kwargs))

  def describe_device(self):
    return "{} name=[{}] mode=[{}]".format(
        self.recorder.__class__.__name__, self.recorder.name, self.mode)

  def playback(self, *args, rval, **kwargs):
    return rval

  def record(self):
    super().record(notes={'name': self.recorder.name}, when=When.NA)

  def recordable(self, track_title):
    '''A Recorder can only record its information to the header track.
    '''
    return track_title == 'header'
