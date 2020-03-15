
import git

from .device import Device
from .manager import RecordableDeviceManager
from .when import When


class Repository(RecordableDeviceManager):
  '''Record interesting things about git repositories.

      Note: This class / module does not provide any decorators.
  '''

  def __init__(self, recorder):
    '''Construct the Repository with a reference to the Recorder on which we
        will record things.

      Args:
        recorder (Recorder): Recorder instance.
    '''
    self._state_recorder = RepositoryState(recorder=recorder)

  def get_states(self, paths=['.']):
    '''Get the state of one or more repositories.

      This does not record the states.

      Usage:
        rekorder.repository.get_states(paths=[
          'path/to/some/repository',
          'path/to/other/repository'
        ])

      Args:
        paths (list[str]): List of paths to capture the state of.

      Returns
        list[dict]: List of dictionaries describing repositories' state.

    '''
    return [self._get_repository_state(path) for path in paths]

  def record(self, paths=['.']):
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
    self._state_recorder(tunes={'repositories': self.get_states(paths)})

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


class RepositoryState(Device):
  '''Record the state of one or more repositories.
  '''

  def __call__(self, tunes):
    self.record(tunes=tunes, when=When.NA)

  def recordable(self, track_title):
    '''Is this device recordable for the named track?
    '''
    return track_title in ['recording', 'header', 'trailer']
