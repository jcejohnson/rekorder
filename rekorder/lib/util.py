import importlib


def load_class(device_description):
  module = importlib.import_module(device_description['module'])
  cls = getattr(module, device_description['class'])
  return cls
