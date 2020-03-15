# rekorder changelog

0.2.0
-----
- Initial playback implementation.
- Initial validate-on-playback impelementation (only tested on ex001.py thus far).
- Bugfix: If mutable parameters change during function invocation MethodParameters recorded the new/changed value for both before and after.
- Capture some thoughts on custom devices.
- Make decorator's wrapper_inner function more DRY.
- Move lib.recorder.py to lib.recorder
- Remove a bunch of dumb delegation methods

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
