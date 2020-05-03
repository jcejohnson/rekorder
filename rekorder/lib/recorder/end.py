
from ..method import MethodReturn
from ..what import What


class RecordingEnd(MethodReturn):
  '''Declare the end of a recording.

      This is optional.
      If an exception is thrown it won't be called.

      Always invoked after method invocation.

      Args:
        None

      Usage:

        @rekorder.end
        def some_func(...):
  '''

  # Device

  def describe_device(self):
    if self.mode in [What.PLAYBACK, What.DESCRIBE]:
      return super().describe_device() + " @ [{}]".format(self.timestamp.localtime)
    return super().describe_device()

  def playback(self, *args, **kwargs):
    if kwargs['rval'] != self.function['rval']:
      raise Exception("Expected [{}] got [{}]".format(self.function['rval'], kwargs['rval']))
    return kwargs['rval']

  def record(self, *args, **kwargs):

    assert self.recorder.recording_medium.track_manager.tracks.current_track.title == 'recording'
    self.recorder.recording_medium.track_manager.set_track('exit')

    super().record(*args, **kwargs)
    if self.mode == What.VALIDATE:
      return

    self.recorder.recording_medium.track_manager.set_track('trailer')

  def validate(self, *args, **kwargs):
    super().validate(*args, **kwargs)
    self.recorder.recording_medium.track_manager.set_track('trailer')

  def recordable(self, track_title):
    '''RecordingBegin can only record its information to the header track.
    '''
    return track_title == 'exit'
