
import json

from .device import Device
from .manager import RecordableDeviceManager
from .medium import RecordingMedium
from .state import SimpleState
from .what import What


class Cassette(RecordingMedium, Device):
  '''A Cassette contains recordings of sipmle CLI apps.

      A Cassette is written to by a Recorder in RECORD mode and
      read from by a Recorder in PLAYBACK mode.

      The events are recorded three states:
        header    : Things that happen before recorder.begin
        recording : Things that happen after recorder.begin and before recorder.end
        trailer   : Things that happen after recorder.end

      Playback similarly progresses through three states:
        header    : Configure the environment using the recorded header
                    e.g. - clone a repo and checkout a specific branch/commit/tag.
        playback  : Playback the recorded events
                    e.g. - Invoke methods, check results, etc.
        trailer   : Restore the environment using the recorded trailer
                    e.g. - checkout a specific branch/commit/tag to restore repository state.
  '''

  # TODO : Consider moving most of the implementation into RecordingMedium

  @staticmethod
  def playback_instance(cls, mode, tune, *args, **kwargs):
    '''Construct a recorded Cassette instance for playback or describe.
    '''
    return Cassette(mode=mode, **tune['data'])

  class RecordingState(SimpleState):

    def __init__(self):
      super().__init__(states=['header', 'recording', 'trailer'])

  class PlaybackState(SimpleState):

    def __init__(self):
      super().__init__(states=['header', 'playback', 'trailer'])

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

    self.state = self._get_state_for_mode()

    if self.mode == What.DESCRIBE:
      return

    # Build a list of dicts based on the current state state.
    self._all_events = [{s: []} for n, s in enumerate(self.state.states)]

    # The initial list of events is the header state.
    initial_state = self.state.states[0]
    self._events = self._all_events[0][initial_state]
    self._current_track = self._events

    self._json_kwargs = {'sort_keys': True, 'indent': 2}

    self.states.append(initial_state)
    self.record(device=self, tunes={'input': self.input, 'output': self.output}, timestamp=kwargs['timestamp'])

  def playback(self):
    '''Read the tunes from storage.

        Reads the entire input file and returns the result
        as a list of dicts.
    '''
    with open(self.input, 'r') as f:
      return json.load(f)

  def begin_recording(self):
    self.state.next()
    self._events = self._all_events[1][self.state.current]
    self._current_track = self._events

  def end_recording(self):
    self.state.next()
    self._events = self._all_events[2][self.state.current]
    self._current_track = self._events

  def record(self, device, tunes, timestamp):
    '''Record an interesting event and save the event stream.

        Invokes write() to ensure that events are not lost.

        The output file will contain a json document that is a
        list of objects (dicts).
    '''

    # if hasattr(recordable, 'function'):
    #   print("{}.record(self, {}, function={})".format(self, recordable, recordable.function))
    # else:
    #   print("{}.record(self, {}, ...)".format(self, recordable))

    blob = {}

    # It is the Recorder's job to timestamp the recordings.
    # t = time.time()
    # blob['time'] = {'time': t, 'localtime': time.asctime(time.localtime(t))}

    blob['data'] = self._record(tunes)
    blob['timestamp'] = {
        'time': timestamp.time,
        'localtime': timestamp.localtime
    }

    if device:
      blob.update(self._record_device(device))

    self._current_track.append(blob)
    self._write(device)

  def _record(self, tunes):
    # TODO - Make this smarter.
    for key, value in tunes.items():
      if value == None:
        tunes[key] = value
      elif isinstance(value, dict):
        tunes[key] = value
      elif isinstance(value, list) or isinstance(value, set) or isinstance(value, tuple):
        tunes[key] = list(value)
      elif isinstance(value, int) or isinstance(value, float) or isinstance(value, str):
        tunes[key] = value
      else:
        tunes[key] = str(value)

      return tunes

  def _record_device(self, device):

    result = {}

    # key = device.__class__.mro()[-2].__name__

    if not isinstance(device, Device):
      raise Exception("[{}] is must be a Device".format(device))

    # Our current RecordingState may not be a state in which the Device can
    # be recorded.
    # For instance, it makes no sense to record method parameters during the
    # header (configuration) state. There is no way to use that information
    # to configure the system on playback.
    if self.state.current not in device.states:
      raise Exception("[{}] is not in states [{}] of device [{}]".format(
          self.state.current, device.states, device))

    # Capture the module and class so that we can construct on playback.
    result['device'] = {
        'module': device.__class__.__module__,
        'class': device.__class__.__name__
    }

    return result

  def _get_state_for_mode(self):

    mode = self.mode

    if mode == What.RECORD:
      if not self.output:
        raise Exception("output required when recording.")
      return Cassette.RecordingState()

    if mode == What.PLAYBACK:
      if not self.input or not self.output:
        raise Exception("input and output required won playback.")
      return Cassette.PlaybackState()

    if mode == What.DESCRIBE:
      return None

    raise Exception("Unknown mode : [{}]".format(mode))

  # Device

  def describe_device(self):
    return "{} output=[{}]".format(self.__class__.__name__, self.output)

  # Internals

  def _write(self, device):
    '''Write (save) the current event stream to the file.
    '''

    class RecordingEncoder(json.JSONEncoder):
      '''JSONEncoder implementation that is aware of rekorder objects.
      '''

      def default(self, obj):
        '''json.JSONEncoder default encoding method.
        '''

        from .when import When

        if isinstance(obj, When):
          return str(obj)

        from .recorder import Recorder

        if isinstance(obj, Recorder):
          raise Exception("Cannot record a Recorder instance."
                          "Check your [{}] recording data.".format(device))

        return json.JSONEncoder.default(self, obj)

    with open(self.output, 'w') as f:
      try:
        json.dump(self._all_events, f, cls=RecordingEncoder, **self._json_kwargs)
      except TypeError as e:
        raise Exception(self._all_events) from e
