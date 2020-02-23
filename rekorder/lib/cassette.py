
import json

from .device import Device
from .manager import RecordableDeviceManager
from .medium import RecordingMedium
from .track_manager import TrackManager
from .tune import Tune
from .what import What


class Cassette(RecordingMedium, Device):
  '''A Cassette contains recordings of sipmle CLI apps.

      A Cassette is written to by a Recorder in RECORD mode and
      read from by a Recorder in PLAYBACK mode.
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

      self._json_kwargs = {'sort_keys': True, 'indent': 2}
      self._track_manager = TrackManager(mode=self.mode)

      # Device

      tune = Tune(
          device=self,
          notes={'input': self.input, 'output': self.output}
      )

      self.record(tune)

    elif self.mode in [What.DESCRIBE, What.PLAYBACK]:

      # When we are constructed via playback_instance() during playback
      # self.input will be None because there was no input provided in record
      # mode.
      if self.input:
        with open(self.input, 'r') as f:
          tracks = json.load(f)
          self._track_manager = TrackManager.playback_instance(tracks, mode=self.mode)

  @property
  def tracks(self):
    return self._track_manager.tracks

  def next_track(self):
    '''Delegate to the track manager so that we don't expose the track manager
        to the recordable devices.
    '''
    self._track_manager.next

  def record(self, tune):
    '''
      Verify that the tune's device can record in our current state.
      Append the tune to the list current track.
      Write everything to the output file.
    '''

    current_track = self._track_manager.current

    if tune.device:
      # Our current RecordingState may not be a state in which the Device can
      # be recorded.
      # For instance, it makes no sense to record method parameters during the
      # header (configuration) state. There is no way to use that information
      # to configure the system on playback.
      if not tune.device.recordable(current_track.title):
        raise Exception("[{}] is not in states [{}] of device [{}]".format(
            current_track.title, tune.device.states, tune.device))

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

        # from .recorder import Recorder

        # if isinstance(obj, Recorder):
        #   raise Exception("Cannot record a Recorder instance."
        #                   "Check your [{}] recording data.".format(device))

        return json.JSONEncoder.default(self, obj)

    with open(self.output, 'w') as f:
      try:
        json.dump(self._track_manager, f, cls=RecordingEncoder, **self._json_kwargs)
      except TypeError as e:
        raise Exception(self._track_manager) from e
