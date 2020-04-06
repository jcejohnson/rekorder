
import git

from ..device import Device
from ..oneshot import OneShot
from ..when import When


class RepositoryState(Device):
  '''Record the state of one or more repositories.
  '''

  @staticmethod
  def playback_instance(cls, *args, **kwargs):
    # This is used by Tune.playback_instance() when the TrackManager
    # is building its list of tunes from recorded data.

    from . import RepositoryManager

    obj = Device.playback_instance(cls, *args, **kwargs)
    obj._repositories = kwargs['repositories']

    manager = RepositoryManager(repository_state=obj)
    return manager

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
    for repository in self._repositories:
      repo = git.Repo(repository['path'])
      target = repository['branch'] \
          if repository['branch'] else \
          repository['tags'][0] if len(repository.get('tags', [])) == 1 else repository['commit']['sha']
      repo.git.checkout(target)
    return rval

  @OneShot
  def record(self, notes, when=When.NA):
    self._repositories = notes['repositories']
    super().record(notes=notes, when=When.NA)

  def recordable(self, track_title):
    '''Is this device recordable for the named track?
    '''
    return track_title in ['recording', 'header', 'trailer']

  def _get_repository_state(self, path):
    repo = git.Repo(path)

    if repo.head.is_detached:
      upstream = None
      reference = None
      commit = repo.head.commit
    else:
      reference = repo.head.reference
      commit = reference.commit
      upstream = reference.tracking_branch()

    repo_data = {
        'path': path,
        'head': repo.head.name,
        'branch': reference.name if reference else None,
        "tags": [str(tag) for tag in repo.tags if tag.commit == repo.head.commit],
        "branches": [str(branch) for branch in repo.branches if branch.commit == repo.head.commit],
        'commit': {
            'author': {
                'name': commit.author.name,
                'email': commit.author.email
            },
            'message': commit.message,
            'sha': commit.hexsha,
        } if commit else {}
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
    from . import RepositoryManager
    if isinstance(other, RepositoryManager):
      other = other.repository_state
    return type(self) == type(other) and self._repositories == other._repositories
