'''Illustrates basic rekorder usage.
'''

import os
import sys
from rekorder import Recorder, When

# Get a named Recorder instance.
recorder = Recorder.get_recorder(
    name=os.path.basename(__file__).replace('.py', ''),
    output=os.path.basename(__file__).replace('.py', '.json'))

print("Application recorder is [{}]".format(recorder))


@recorder.begin  # Start recording when main() is called.
#                # This also captures the method's parameters.
@recorder.end    # End the recording when main() returns.
#                # This also captures the method's result.
def main():
  foo(1, 2, 3, foo='bar', bar='baz')


@recorder.method.params         # Capture foo's parameters before invocation.
@recorder.method.pass_recorder  # This should be "closest" to the function
#                               # because a Recorder cannot be serialized.
def foo(rec, *args, **kwargs):

  print("foo recorder is [{}]".format(rec))

  # Add a comment to the recording.
  # This is not yet implemented.
  # recorder.comment("Coming to you from foo()")

if __name__ == "__main__":

  # The replayable recording doesn't start until the @recorder.begin
  # function is invoked. Any recorded information prior to that will
  # be used as playback configuration.

  if len(sys.argv) > 1:
    # Capture the state of one or more repositories in the recording's
    # header (configuration) section.
    # On playback the repositories will be cloned and checked out at
    # the recorded commit.
    recorder.repository_state.record(paths=sys.argv[1:])

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
