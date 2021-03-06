
from .. import util
from ..method import MethodParameters
from ..when import When
from ..what import What


class RecordingBegin(MethodParameters):
  '''Declare the beginning of a recording.

      Every recording must have one of these.
      Anything recorded prior to this is considered configuration / setup.

      Always invoked before method invocation.

      Args:
        None

      Usage:

        @rekorder.before
        def some_func(...):
  '''

  # Device

  def describe_device(self):
    if self.mode in [What.PLAYBACK, What.DESCRIBE]:
      return super().describe_device() + " @ [{}]".format(self.timestamp.localtime)
    return super().describe_device()

  def playback(self, *args, **kwargs):
    print("** Beginning playback")
    f = util.load_function(self.function)
    args = self.function['args']
    kwargs = self.function['kwargs']
    r = f(*args, **kwargs)
    print("** Playback complete")
    return r

  def record(self, *args, **kwargs):

    # RecordingBegin.record() must be called either during the 'header' track or the 'entry' track.
    # If called in the 'header' track (e.g. - when self.mode == What.RECORD) we advance to the
    # 'entry' track automatically.
    assert self.recorder.recording_medium.track_manager.tracks.current_track.title in ['header', 'entry']
    self.recorder.recording_medium.track_manager.set_track('entry')

    # Device will bind _our_ record() method to Device.__validate__ when self.mode == What.VALIDATE
    # but when we call super().record() we will get the real baseclass method (i.e. - Device.record)
    # For any other mode, our record() method remains as is.
    super().record(*args, **kwargs)

    if self.mode == What.VALIDATE:
      # Do not advance to the 'recording' track in validate mode.
      # We need to remain in 'entry' mode until validate() has had a chance to execute.
      return

    # After our state has been recorded we tell the recorder to move on to the 'recording' track
    # where everything else will be recorded until RecordingEnd fires.
    self.recorder.recording_medium.track_manager.set_track('recording')

  def validate(self, *args, **kwargs):
    '''
    We've already established that RecordingBegin is "special"...
    player._playback_body() will fetch the next tune from the entry track.
    Fetching the next tune from any track will set that track's current_tune to that value.
    That tune is the recording of RecordingBegin.
    Now, when player._playback_body() invokes playback() on the RecordingBegin tune we will
    evetually wind up here to validate that the current attempt to RecordingBegin matches
    the recorded value.
    Because player._playback_body() already fetched that (one and only one) tune from the
    entry track we need to reset the track to its original state so that super().validate()
    will fetch from the beginning of the list of tunes.
    '''
    tune = self.recorder.recording_medium.track_manager.current_track.reset()

    super().validate(*args, **kwargs)
    self.recorder.recording_medium.track_manager.set_track('recording')

  def recordable(self, track_title):
    '''RecordingBegin can only record its information to the header track.
    '''
    return track_title == 'entry'

  def __call__(self, function):
    # Only allow When.BEFORE. Do not allow parameters.
    return super().__call__(function=function, when=When.BEFORE)
