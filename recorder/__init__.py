
'''recorder is a module for recording interesting tunes.

  FUTURE:
  - Implement a playback mechanism.
  - Compare recordings (e.g. - for validating tests).

  Usage:

    import recorder

    # Capture the repository state before calling the function
    @recorder.method.repository_state
    # Capture the method parameters
    @recorder.method.param
    # Capture the method return value
    @recorder.method.rval
    # Capture exceptions thrown by the method (rethrown wrapped by recorderExceptionWrapper)
    @recorder.method.exception
    def some_func(...):
      ...

    # This will record the same as above but in a different order:

    @recorder.method.rval
    @recorder.method.repository_state
    @recorder.method.param
    @recorder.method.exception
    def some_func(...):
      ...

    # recorder.method.repository_state and recorder.method.param take an optional `when`
    # parameter. Possible values are:
    #    recorder.When.BEFORE  : Record before calling the function
    #    recorder.When.AROUND  : Record before and after calling the function
    #    recorder.When.AFTER   : Record after calling the function
    #
    # recorder.method.rval does not support this since we have to call the function
    # to get the return value.

    # Capture the repository state before and after calling the function
    @recorder.method.repository_state(when=recorder.When.AROUND)
    # Capture the method parameters
    @recorder.method.param
    # Capture the method return value
    @recorder.method.rval
    # Capture exceptions thrown by the method (rethrown wrapped by recorderExceptionWrapper)
    @recorder.method.exception
    def some_other_func(...):
      ...

    def main():

      recorder.initialize(path='greatest-hits.json')

      # Capture the state of some repositories:
      recorder.repository_state(func=main, paths=['path/to/some/repository'])

  See also:

    recorder.method
    recorder.repository


'''


from . import method
from . import exception_wrapper
from .cassette import Cassette
from .repository import repository_state
from .when import When


def initialize(path):
  '''Initialize the recording session by providing a file path in which to record the tunes.
  '''
  return Cassette.initialize(path)
