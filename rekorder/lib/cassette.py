
import json

from .device import Device
from .medium import RecordingMedium
from .track import TrackManager
from .tune import Tune
from .what import What


class Cassette(RecordingMedium, Device):
  '''A Cassette contains recordings of sipmle CLI apps.

      A Cassette is written to by a Recorder in RECORD mode and
      read from by a Recorder in PLAYBACK mode.

      FIXME: Cassette should not be a Device.
             Use DeviceProxy like RepositoryManager or
             a CassetteDevice like Recorder/RecordingDevice.
  '''

  # TODO : Consider moving most of the implementation into RecordingMedium

  def __init__(self, *args, **kwargs):
    '''Construct the Cassette.

      A Cassette contains an internal collection of events.

      In record mode this list will be written to the output on every
      call to the record() function.

      Args:
        input (str): Path from which recorded data is read for playback
                     or describe.
        output (str): Path at which to record or from which to playback.
        mode (enum): rekorder.What.RECORD or rekorder.What.PLAYBACK
    '''

    super().__init__(*args, **kwargs)

    self.input = kwargs['input'] if 'input' in kwargs else None
    self.output = kwargs['output'] if 'output' in kwargs else None

    if self.mode == What.RECORD:
      self._init_for_record(*args, **kwargs)

    elif self.mode == What.DESCRIBE:
      self._init_for_describe(*args, **kwargs)

    elif self.mode == What.PLAYBACK:
      self._init_for_playback(*args, **kwargs)

    else:
      raise Exception("Unsupported mode [{}]".format(self.mode))

  def _init_for_record(self, *args, **kwargs):

    self._json_kwargs = {'sort_keys': True, 'indent': 2}
    self.track_manager = TrackManager(mode=self.mode)

    # Device

    tune = Tune(
        device=self,
        notes={'input': self.input, 'output': self.output}
    )

    self.record(tune)

  def _init_for_describe(self, *args, **kwargs):
    self._init_for_playback(*args, **kwargs)

  def _init_for_playback(self, *args, **kwargs):

    # This is a little confusing.
    #
    # player.describe()/playback() will create a Cassette instance.
    #
    # During the describe/playback operation _another_ Cassette instance
    # will be created because the record-time Cassette data is saved in the
    # input file. This second instance will be created in playback mode the
    # same as every other Device. The recorded Cassette's tunes includes the
    # record-time output filename but not an input filename. This is why we
    # have a guard on self.input here.
    if not self.input:
      return

    # Disable the record() method.
    # We cannot record and playback at the same time!
    self.record = self._record_in_playback_mode
    self._write = None

    with open(self.input, 'r') as f:
      tracks = json.load(f)
      self.track_manager = TrackManager.playback_instance(tracks, mode=self.mode)

  def playback(self, *args, rval, **kwargs):
    return rval

  def _record_in_playback_mode(self, tune):
    self.last_tune = tune

  def record(self, tune):
    '''
      Verify that the tune's device can record in our current state.
      Append the tune to the list current track.
      Write everything to the output file.
    '''

    current_track = self.track_manager.current_track

    if tune.device:
      # Our current RecordingState may not be a state in which the Device can
      # be recorded.
      # For instance, it makes no sense to record method parameters during the
      # header (configuration) state. There is no way to use that information
      # to configure the system on playback.
      if not tune.device.recordable(current_track.title):
        raise Exception("[{}] is not recordable on track [{}]".format(
            tune.device, current_track.title))

    current_track.add(tune)

    self._write()

  # Device

  def describe_device(self):
    return "{} output=[{}]".format(self.__class__.__name__, self.output)

  def recordable(self, track_title):
    '''A Cassette can only record its information to the header track.
    '''
    return track_title == 'header'

  # Internals

  def _write(self):
    '''Write (save) the current event stream to the file.
    '''

    class RecordingEncoder(json.JSONEncoder):
      '''JSONEncoder implementation that is aware of rekorder objects.
      '''

      def default(self, obj):
        '''json.JSONEncoder default encoding method.
        '''

        f = getattr(obj, 'recordable_data', None)
        return f(obj) if f else json.JSONEncoder.default(self, obj)

    with open(self.output, 'w') as f:
      try:
        json.dump(self.track_manager, f, cls=RecordingEncoder, **self._json_kwargs)
      except TypeError as e:
        raise Exception(self.track_manager) from e
