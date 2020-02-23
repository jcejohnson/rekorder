# rekorder changelog

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
