
import sys
import recorder


def main():

  recorder.initialize(path='greatest-hits.json')

  @recorder.method.param(when=recorder.When.AROUND)
  @recorder.method.repository_state(paths=[sys.argv[1]], when=recorder.When.AROUND)
  @recorder.method.rval
  @recorder.method.exception
  def foo():
    10 / 2

  @recorder.method.repository_state
  @recorder.method.param
  @recorder.method.rval
  @recorder.method.exception
  def bar():
    0 / 0

  @recorder.method.everything(when=recorder.When.AFTER)
  def baz(a, b, c=99):
    print("baz!!!")
    return a / b

  print(__name__)
  print("Hello")
  # foo()
  baz(25, 5, 9)
  # baz(25, b=5, c=9)
  # baz(b=5, a=15)
  print("Goodbye")

  print(baz)

  # recorder.repository_state(func=main, paths=[sys.argv[1]])

  # bar()

if __name__ == "__main__":
  main()
