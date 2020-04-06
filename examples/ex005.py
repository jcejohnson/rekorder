#!venv/bin/python

'''Illustrates basic rekorder usage plus repository.
'''

import git
import os
import sys
from rekorder import Recorder, When, What

test_repo = 'examples/rekorder'

# Get a named Recorder instance.
recorder = Recorder.get_recorder(
    name=os.path.basename(__file__).replace('.py', ''),
    output=os.path.basename(__file__).replace('.py', '.json'))

if recorder.mode == What.RECORD:
  print("Application recorder is [{}]".format(recorder))


@recorder.begin  # Start recording when main() is called.
#                # This also captures the method's parameters.
@recorder.end    # End the recording when main() returns.
#                # This also captures the method's result.
def main():
  repo = git.Repo(test_repo)
  print("Begin [{}] @ [{}]".format(__name__, repo.head.commit.hexsha))
  foo(1, 2, 3, foo='bar', bar='baz')
  bar()
  print("End [{}] @ [{}]".format(__name__, repo.head.commit.hexsha))


@recorder.method.repository(paths=[test_repo])  # Capture test_repo's state before invocation.
def foo(*args, **kwargs):

  repo = git.Repo(test_repo)
  print("repo.head.commit.hexsha : [{}]".format(repo.head.commit.hexsha))
  assert str(repo.head.commit.hexsha) == '4909eb712b09dae3b2cc324cbfdb96af7ab0868f'


@recorder.method.pass_recorder
def bar(rec, *args, **kwargs):

  # Capture test_repo's state during invocation.
  rec.repository_manager.record(paths=[test_repo])

  # A RepositoryManager instance can be used only once.
  # Caching it in a temporary variable is fine but if we try to use
  # that to record multiple times we will get an exception.
  r = rec.repository_manager
  r.record(paths=[test_repo])
  try:
    r.record(paths=[test_repo])
  except Exception as e:
    r = None
  if r:
    raise Exception("Did not get expected repository_manager reuse exception.")

  repo = git.Repo(test_repo)
  print("repo.head.commit.hexsha : [{}]".format(repo.head.commit.hexsha))

if __name__ == "__main__":

  # TODO: Clone rekorder to examples/rekorder if it doesn't exist.

  # We have a sample repository at `examples/rekorder`
  # Before we start the test we will checkout a particular tag so that we can
  # see if playback will do the same for us.
  repo = git.Repo(test_repo)

  # Record the test repo's state before the main recording begins.
  # A new RepositoryManager is created on each call to repository_manager so
  # we need to cache the one we want to restore_on_playback.
  repository_manager = recorder.repository_manager

  repo.heads['master'].checkout()
  repository_manager.record(paths=[test_repo])

  repo.git.checkout('v0.1.0')

  main()

  repo.heads['master'].checkout()

  # This will add an entry to the trailer of our recording so that on playback
  # test_repo will be returned to master instead of wherever main() may have
  # put it.
  repository_manager.restore_on_playback()
