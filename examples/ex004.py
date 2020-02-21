'''Illustrate basic / typical usage of Recorder.
'''

import os
import sys
from rekorder import Recorder, When


def main(recorder):
  print("Hello World")

  # playback = recorder.playback_config()
  # playback.repository.clone(paths=[sys.argv[1]])

  @recorder.method.params(when=When.AROUND)
  # @recorder.method.repository_state(paths=[sys.argv[1]], when=When.AROUND)  # Not yet implemented
  @recorder.method.rval
  @recorder.method.exception
  def foo(*args, **kwargs):
    print("foo")
    10 / 2

  # @recorder.method.repository_state  # Not yet implemented
  @recorder.method.params
  @recorder.method.rval
  @recorder.method.exception
  def bar():
    0 / 0

  # @recorder.method.everything(when=When.AFTER)
  @recorder.method.params(when=When.AROUND)
  @recorder.method.rval
  @recorder.method.exception
  # @recorder.method.mockme  # Replace with a mock object in playback
  def baz(a, b, c=99):
    print("baz!!!")
    foo(c)
    return a / b

  print(__name__)
  print("Hello")
  foo()

  print("baz method is [{}]".format(baz))
  baz(25, 5, 9)
  baz(25, b=5, c=9)
  baz(b=5, a=15)

  if len(sys.argv) > 1:
    print("Recording state of repository [{}]".format(sys.argv[1]))
    recorder.repository_state.record(paths=[sys.argv[1]])

  print("Testing exception handling")
  try:
    bar()
  except ZeroDivisionError as e:
    print("Caught expected ZeroDivisionError")

if __name__ == "__main__":

  recorder = Recorder(name="MyRekorder", output=os.path.basename(sys.argv[0]).replace('.py', '.json'))

  @recorder.begin
  @recorder.end
  @recorder.method.params(when=When.AROUND)
  @recorder.method.rval
  @recorder.method.exception
  def main_wrapper():
    main(recorder)

  main_wrapper()