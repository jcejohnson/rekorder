
import inspect


def show(stuff):
  for thing in stuff:
    print(thing)


def bar():
  print("bar")

  def baz():
    print("baz")

  baz()

  print("about baz")
  show(inspect.getmembers(baz))

if __name__ == '__main__':
  bar()

  print("about bar")
  show(inspect.getmembers(bar))
