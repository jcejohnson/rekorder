#!venv/bin/python

'''Illustrates basic rekorder usage with mock-on-playback.
'''

import os
import random
import sys
from rekorder import Recorder, When, What

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
  print("Begin [{}]".format(__name__))
  r = foo(1, 2, 3, foo='bar', bar='baz')
  print("End [{}] [{}]".format(__name__, r))


@recorder.method.params          # Capture foo's parameters before invocation.
@recorder.method.rval(mock=True)  # Capture foo's return value.
@recorder.method.pass_recorder   # This should be "closest" to the function
#                                # because a Recorder cannot be serialized.
def foo(rec, *args, **kwargs):

  r = random.randrange(1000)

  print("I am foo and I will return [{}]".format(r))

  return r

if __name__ == "__main__":

  # Note that we cannot do any recorder actions here if we are going to do
  # playback verification because this will not be executed during playback.
  # (because __name__ won't be "__main__")

  main()
