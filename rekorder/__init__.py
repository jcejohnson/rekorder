
'''rekorder is a module for recording interesting tunes.

  FUTURE:
  - Implement a playback mechanism.
  - Compare recordings (e.g. - for validating tests).

  Usage:

    from rekorder import Recorder, When

    rekorder = Recorder(path='greatest-hits.json')

    # Capture the repository state before calling the function
    @rekorder.method.repository_state
    # Capture the method parameters
    @rekorder.method.param
    # Capture the method return value
    @rekorder.method.rval
    # Capture exceptions thrown by the method (rethrown wrapped by rekorderExceptionWrapper)
    @rekorder.method.exception
    def some_func(...):
      ...

    # This will record the same as above but in a different order:

    @rekorder.method.rval
    @rekorder.method.repository_state
    @rekorder.method.param
    @rekorder.method.exception
    def some_func(...):
      ...

    # rekorder.method.repository_state and rekorder.method.param take an optional `when`
    # parameter. Possible values are:
    #    When.BEFORE  : Record before calling the function
    #    When.AROUND  : Record before and after calling the function
    #    When.AFTER   : Record after calling the function
    #
    # rekorder.method.rval does not support this since we have to call the function
    # to get the return value.

    # Capture the repository state before and after calling the function
    @rekorder.method.repository_state(when=When.AROUND)
    # Capture the method parameters
    @rekorder.method.param
    # Capture the method return value
    @rekorder.method.rval
    # Capture exceptions thrown by the method (rethrown wrapped by RecorderExceptionWrapper)
    @rekorder.method.exception
    def some_other_func(...):
      ...

    # Capture the state of some repositories:
    rekorder.repository_state(paths=['path/to/some/repository'])

'''


from .lib.player import Player
from .lib.recorder import Recorder
from .lib.what import What
from .lib.when import When
