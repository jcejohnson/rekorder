# rekorder changelog

0.3.0
-----
- Added DeviceProxy marker interface for classes that want to proxy (wrap) Device instances.
- Added CliState recorder to record & restore sys.argv so that target app sees original sys.argv rather than playback's sys.argv.
- Initial implementation of header & trailer tracks repository playback (does not clone/checkout).
- Validate-on-playback of recording track working for ex001 - ex004 (all functions).
- Shifted repository state mechanics from RepositoryManager to RepositoryState(Device).
- Moved validation failure exception in Device.validate() to validation_failure() function so that derived classes can override it.
*Breaking Changes*
- @rekorder.method.repository_state decorator is now @rekorder.method.repository
- Recorder.repository_state is now Recorder.repository_manager
- repository.Repository class is now repository.RepositoryManager

0.3.0
-----
- Initial playback implementation.
- Initial validate-on-playback implementation (only tested on ex001.py in this version).
- Bugfix: If mutable parameters change during function invocation MethodParameters recorded the new/changed value for both before and after.
- Capture some thoughts on custom devices.
- Make decorator's wrapper_inner function more DRY.
*Breaking Changes*
- Move lib.recorder.py to lib.recorder
- Remove a bunch of dumb delegation methods.

0.1.1
-----
- Document recordings file format.
- Introduce Tune to abstract/manage the Device & tunes relationship.
- Simplify record() methods to take a Tune() instead of separate device & tunes elements.
- Simplify player.describe by leveraging Tune's ability to reconstruct recorded Devices and their Notes.
- Introduce TrackManager to manage what was previously recording states.
- Introduce 'entry' and 'exit' tracks (states) around 'recording' for use by RecordingBegin and RecordingEnd. Cleanup how we manage begin & end.
- Replace Recorder and Cassette begin_recording/end_recording with next_track.
- Introduce recordable_data() static method for use by our custom JSONEncoder.
- In Decorator, add pre/post methods for invoke and record to give derived classes more control.
- Replace Device.states list with Device.recordable(track) method.
- Added .bumpversion.cfg

0.1.0
-----
- Initial release
- Basic record & describe functionality
