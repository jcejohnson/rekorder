

class DeviceProxy:
  '''A marker interface to indicate that an object can be used in place
      of a Device.

      DeviceManager classes will generally contain one or more
      Device instances.
      In some cases (e.g. - repository.RepositoryState) it is desirable for
      the device's playback_instance() method to return an instance of the
      DeviceManager instead of the Device. When this is done,
      the DeviceManager must derive from DeviceProxy so that the
      system (e.g. - Tune) will treat it as a Device.

      Deriving DeviceManager classes from DeviceProxy is preferred
      to deriving them from Device because it allows for a better separation
      of concerns by separating the Device details in a second / helper class
      rather than overloading the DeviceManager itself.
  '''
  pass
