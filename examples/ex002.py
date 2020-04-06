#!venv/bin/python

'''Illustrates non-decorator usage.
'''

import os
import sys
from rekorder import Recorder, When, What


def main():
  print("Hello World")


if __name__ == "__main__":

  # Get a named Recorder instance.
  recorder = Recorder.get_recorder(
      name=os.path.basename(__file__).replace('.py', ''),
      output=os.path.basename(__file__).replace('.py', '.json'))

  print("Application recorder is [{}]".format(recorder))

  # Instead of using decorators as the other examples do, we can "manually"
  # decorate the function by invoking the decorator functions.
  # This is a bit of an odd usecase but might be handy if you cannot create
  # a global recorder instance or cannot use the decorators normally.
  main = recorder.begin(main)
  main = recorder.end(main)

  main()

else:  # If we _don't_ want to do playback verification, we _don't_ need this.

  # CLI apps generally don't have an `else` for their check against __name__.
  # However, for playback verification to work, we need to wrap main() in this
  # state just as we did when recording. If we don't do this, the tracks will
  # be out of sync and verification will fail.

  # Get a named Recorder instance.
  recorder = Recorder.get_recorder(
      name=os.path.basename(__file__).replace('.py', ''),
      output=os.path.basename(__file__).replace('.py', '.json'))

  main = recorder.begin(main)
  main = recorder.end(main)
