'''Illustrates usage of Recorder and Method as RecordableDevices
'''

import os
import sys
from rekorder import Recorder, When


def main():
  print("Hello World")


if __name__ == "__main__":

  # Get a named Recorder instance.
  recorder = Recorder.get_recorder(name=__name__, output=os.path.basename(sys.argv[0]).replace('.py', '.json'))

  # The replayable recording doesn't start until the @recorder.begin
  # function is invoked. Any recorded information prior to that will
  # be used as playback configuration.

  if len(sys.argv) > 1:
    # Capture the state of one or more repositories in the recording's
    # header (configuration) section.
    # On playback the repositories will be cloned and checked out at
    # the recorded commit.
    recorder.repository_state.record(paths=sys.argv[1:])

  # Instead of using decorators as the other examples do, we can "manually"
  # decorate the function by invoking the decorator functions.
  # This is a bit of an odd usecase but might be handy if you cannot create
  # a global recorder instance or cannot use the decorators normally.
  main = recorder.begin(main)
  main = recorder.end(main)

  main()

  # The recordable recording stops when the @recorder.end function
  # is invoked. Anything recorded after that will be used to restore
  # the workspace during playback.

  if len(sys.argv) > 1:
    # Capture the state of those same repositories in the recording's
    # trailter (restore) section.
    # On playback the repositories will be checked out at the recorded
    # commit. (i.e. - restored to their pre-execution state)
    recorder.repository_state.record(paths=sys.argv[1:])
