
'''Methods for recording repository state.
'''


import git

from .cassette import Cassette


def repository_state(func=None, paths=['.'], recorder=None):
  '''Standalone function (not a decorator) to long the state of one or more repositories.

      :param function func: The function invoking repository_state()
      :param list paths: List of paths to capture the state of.
      :param function recorder: Decorator function (if any) that will provide the 'type' value of the recording.
  '''

  for path in paths:
    blob = _get_repository_state(path)
    Cassette.instance().record(
        recorder=recorder if recorder else repository_state,
        func=func,
        **blob)


def _get_repository_state(path):
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
