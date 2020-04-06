
from ..device import DeviceProxy
from ..device import DeviceManager
from ..oneshot import OneShot
from ..when import When

from .state import RepositoryState


class RepositoryManager(DeviceManager, DeviceProxy):
  '''Record interesting things about git repositories.

      RepositoryManager is used:
      - Directly in a script that is recording its actions via
        recorder.repository_manager.
      - Indirectly by the @rekorder.method.repository decorator.
        See MethodRepository for this usecase.

      Note: This class / module does not provide any decorators.
  '''

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    # This is used by MethodRepository.playback_instance()
    return RepositoryState.playback_instance(RepositoryState, *args, **kwargs)

  def __init__(self, *args, **kwargs):
    '''Construct the Repository with a reference to the Recorder on which we
        will record things.

      Args:
        recorder (Recorder): Recorder instance.
    '''
    if kwargs.get('repository_state', None):
      # When constructed by RepositoryState.playback_instance()
      self.repository_state = kwargs['repository_state']
    else:
      self.repository_state = RepositoryState(recorder=kwargs.get('recorder', None))

    self._notes = None

  def describe_device(self):
    return self.repository_state.describe_device()

  def get_notes(self, paths=['.']):
    self._notes = self.repository_state.get_notes(paths)
    return self._notes

  def playback(self, *args, **kwargs):
    return self.repository_state.playback(*args, **kwargs)

  @OneShot
  def record(self, paths=['.'], when=When.NA):
    '''Record the state of one or more repositories.

      Delgates to the RepositoryState Recordable device

      Usage:
        rekorder.repository.record(paths=[
          'path/to/some/repository',
          'path/to/other/repository'
        ])

      The @OneShot decorator is used to ensure that this method is only ever
      invoked once on this instance. This is important for preserving the state
      of self._notes so that restore_on_playback will restore the expected state.
    '''
    self.repository_state.record(notes=self.get_notes(paths), when=When.NA)

  def restore_on_playback(self):
    if not self._notes:
      raise Exception("Missing notes. Did you forget to call record()?")

    # The RepositoryState record() method is a OneShot method.
    # We know we will have called it in our record() method so we need to tell OneShot
    # that it is OK for it to be called again.
    # We don't want to remove the @OneShot decorator because we still want to be sure
    # that nobody else attempts to call it twice.
    self.repository_state.record(notes=self._notes, when=When.NA, reset_oneshot=True)

  def __eq__(self, other):
    return type(self) == type(other) and self.repository_state == other.repository_state

  def __str__(self):
    return self.repository_state.describe_device()
