
import git

from .device import Device
from .device import DeviceProxy
from .manager import RecordableDeviceManager
from .when import When


class RepositoryManager(RecordableDeviceManager, DeviceProxy):
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

  def describe_device(self):
    return self.repository_state.describe_device()

  def get_notes(self, paths=['.']):
    return self.repository_state.get_notes(paths)

  def playback(self, *args, **kwargs):
    return self.repository_state.playback(*args, **kwargs)

  def record(self, paths=['.'], when=When.NA):
    '''Record the state of one or more repositories.

      Delgates to the RepositoryState Recordable device

      Usage:
        rekorder.repository.record(paths=[
          'path/to/some/repository',
          'path/to/other/repository'
        ])

      Args:
        paths (list[str]): List of paths to capture the state of.
    '''
    self.repository_state.record(notes=self.get_notes(paths), when=When.NA)

  def __eq__(self, other):
    return type(self) == type(other) and self.repository_state == other.repository_state

  def __str__(self):
    return self.repository_state.describe_device()


class RepositoryState(Device):
  '''Record the state of one or more repositories.
  '''

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    # This is used by Tune.playback_instance() when the TrackManager
    # is building its list of tunes from recorded data.
    repository_state = Device.playback_instance(cls, *args, **kwargs)
    repository_state._repositories = kwargs['repositories']
    repository_manager = RepositoryManager(repository_state=repository_state)
    return repository_manager

  def describe_device(self):
    r = "{} {}".format(
        self.__class__.__name__,
        ["{path} @ {commit[sha]:.8}".format(**repo) for repo in self._repositories]
    )
    return r

  def describe_playable_device(self):
    return self.describe_device()

  def describe_recordable_device(self):
    return self.describe_device()

  def get_notes(self, paths=['.']):
    self._repositories = self._get_states(paths)
    return {'repositories': self._repositories}

  def playback(self, *args, rval, **kwargs):
    return rval

  def record(self, notes, when=When.NA):
    self._repositories = notes['repositories']
    super().record(notes=notes, when=When.NA)

  def recordable(self, track_title):
    '''Is this device recordable for the named track?
    '''
    return track_title in ['recording', 'header', 'trailer']

  def _get_repository_state(self, path):
    repo = git.Repo(path)
    upstream = repo.head.reference.tracking_branch()

    repo_data = {
        'path': path,
        'head': repo.head.name,
        'branch': repo.head.reference.name,
        'commit': {
            'author': {
                'name': repo.head.reference.commit.author.name,
                'email': repo.head.reference.commit.author.email
            },
            'message': repo.head.reference.commit.message,
            'sha': repo.head.reference.commit.hexsha,
        }
    }

    if upstream:
      repo_data.update(
          {
              'remote': {
                  'name': upstream.remote_name,
                  'branch': upstream.remote_head,
                  'commit': upstream.commit.hexsha
              }
          }
      )

    return repo_data

  def _get_states(self, paths):
    '''Get the state of one or more repositories.

      This does not record the states.

      Usage:
        rekorder.repository._get_states(paths=[
          'path/to/some/repository',
          'path/to/other/repository'
        ])

      Args:
        paths (list[str]): List of paths to capture the state of.

      Returns
        list[dict]: List of dictionaries describing repositories' state.

    '''
    return [self._get_repository_state(path) for path in paths]

  def __eq__(self, other):
    if isinstance(other, RepositoryManager):
      other = other.repository_state
    return type(self) == type(other) and self._repositories == other._repositories
