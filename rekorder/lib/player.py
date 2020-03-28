
from .cassette import Cassette
from .device import Device
from .recorder.device import RecordingDevice
from .what import What

import importlib


class Player:
  '''Describe and replay recordings.
  '''

  def __init__(self, *args, **kwargs):
    self._recording_medium = Cassette(*args, **kwargs)

  def describe(self):
    '''Describe a recording.
    '''

    for track in self._recording_medium.tracks:
      print(track.title)

      if not len(track.tunes):
        print("  None")
        continue

      for tune in track.tunes:
        print("  {}".format(tune.device))

        if isinstance(tune.device, RecordingDevice):
          if self._recording_medium.recorder:
            raise Exception("Too many recorders")
          self._recording_medium.recorder = tune.device

  def playback(self):
    '''Play back a recording.
    '''

    # Fetch and playback the header track.
    # This will intialize the recorder for playback validation.
    rval = self._playback_header()

    # Fetch and playback the entry track.
    # This will invoke the entry point recorded by RecordingBegin.
    rval = self._playback_body(rval)

    # Playback of the entry track will have taken us through the
    # recording & exit tracks and left us at the trailer.
    rval = self._playback_trailer(rval=rval)

  def _playback_header(self):
    '''Playback the header to configure the workspace state and Recorder.
    '''

    track = self._recording_medium.track_manager.tracks.current_track
    assert track.title == 'header'

    rval = None

    for tune in track.tunes:
      print("  {}".format(tune.device))

      if isinstance(tune.device, RecordingDevice):
        self._engage_validation(tune.device.recorder)

      rval = tune.playback(rval=rval)

    track = self._recording_medium.track_manager.next
    assert track.title == 'entry'

    return rval

  def _playback_body(self, rval):
    '''Playback the entry, recording and exit tracks.
    '''

    track = self._recording_medium.track_manager.tracks.current_track
    assert track.title == 'entry'

    print("")
    print(track.title)

    if track.size() != 1:
      raise Exception("There can be only one.")

    tune = track.next_tune()
    print("  {}".format(tune.device))

    # entry playback will launch the application and move to the 'recording'
    # track. As the application executes, it will consume the recorded tunes
    # and validate the execution against the recording. This includes moving
    # to the 'exit' track and validating the application's exit which then
    # puts us on the 'trailer' track.

    rval = tune.playback(rval=rval)

    track = self._recording_medium.track_manager.tracks.current_track
    assert track.title == 'trailer'

    return rval

  def _playback_trailer(self, rval):
    '''Playback the trailer to restore workspace state.
    '''

    track = self._recording_medium.track_manager.tracks.current_track
    assert track.title == 'trailer'

    for tune in track.tunes:
      print("  {}".format(tune.device))
      rval = tune.playback(rval=rval)

    track = self._recording_medium.track_manager.tracks.current_track
    assert track.title == 'trailer'

    return rval

  def _engage_validation(self, recorder):
    if self._recording_medium.recorder:
      raise Exception("Too many recorders")
    self._recording_medium.recorder = recorder
    recorder.recording_medium = self._recording_medium
    recorder.mode = What.VALIDATE
