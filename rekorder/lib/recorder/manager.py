

from ..device import DeviceManager
from ..when import When

from .begin import RecordingBegin
from .end import RecordingEnd


class RecordingManager(DeviceManager):

  def __init__(self, recorder):
    super().__init__()

    self.recorder = recorder

  #
  # When used as a callable object

  def __call__(self, function=None, *, when=When.AROUND, **kwargs):
    '''Invoked when Recorder is used as a decorator.

      Usage:
        recorder = Recorder.get_recorder(...)

        @rekorder  # Implicitly uses the RecordingBegin and RecordingEnd decorators.
        def some_function(...)
    '''

    # This arrangement replicates:
    #    @rekorder.begin
    #    @rekorder.end
    #    def some_function(...)
    function = self.end(function=function, **kwargs)
    function = self.begin(function=function, **kwargs)
    return function

  @property
  def begin(self):
    '''Invoked when Recorder delegates to the RecordingBegin decorator.

      Usage:
        recorder = Recorder.get_recorder(...)

        @rekorder.begin
        def some_function(...)
    '''
    return RecordingBegin(recorder=self.recorder)

  @property
  def end(self):
    '''Invoked when Recorder delegates to the RecordingEnd decorator.

      Usage:
        recorder = Recorder.get_recorder(...)

        @rekorder.end
        def some_function(...)
    '''
    return RecordingEnd(recorder=self.recorder)
