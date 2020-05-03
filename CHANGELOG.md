# rekorder changelog

0.6.0
-----
- Implement @recorder.method.mock in place of @recorder.method.rval(mock=True)
- Implement [quicktest.sh](quicktest.sh) to execute & playback all of the examples.
*Breaking Changes*
- Revert @recorder.method.rval to v0.4.0 behavior (i.e. - remove _mock_ parameter)

0.5.0
-----
- Implement @recorder.method.rval(mock=True).
  - This disables recording until the function returns.
    (In a future version I hope have a nested track within the MethodReturn tune where mock is True.)
  - On playback, the return value is provided without calling the function.
  - Added ex006 to show basic usage of this
- @recorder.method.rval now records BEFORE and AFTER state. `rval` will always be _null_ at BEFORE.
  (I hope to remove the BEFORE in a future version.)
*Breaking Changes*
- @recorder.method.rval now defaults to When.AROUND.
  Anything deriving from MethodReturn must override `__call__()` to preserve the original behavior. (See RecordingEnd)
- The new `mock` recording state is allowed for all Devices by default.
- Device no longer sets self.when in `__init__()`. self.when is only relevant to methods and now set by `Decorator.__call__()`.
- `Decorator._baa()` now passes _target_ to `self.record(notes=notes, when=target)`. This means record() will get When.BEFORE or When.AFTER instead of When.AROUND.

0.4.0
-----
- Implement RepositoryState.playback() so that MethodRepository.before() can restore the state of repositories during playback validation.
- Rename & relocate for consistency:
  - rekorder/lib/device.py -> rekorder/lib/device/device.py
  - rekorder/lib/manager.py -> rekorder/lib/device/manager.py
  - rekorder/lib/repository.py -> rekorder/lib/repository/state.py
  - rekorder/lib/track_manager.py -> rekorder/lib/track/manager.py
  - rekorder/lib/track.py -> rekorder/lib/track/track.py
- Put each class into its own file to keep things bite-sized.
- RecordableDeviceManager is now DeviceManager.
- Removed the very confusing playback() method from Recorder. RecordingDevice handles playback entirely now.
- Add OneShot wrapper to enforce one-invocation-per-instance for some methods (see RepositoryManager.record())


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

0.2.0
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
