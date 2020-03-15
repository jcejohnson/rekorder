import importlib


def load_class(device_description):
  module = importlib.import_module(device_description['module'])
  cls = getattr(module, device_description['class'])
  return cls


def load_function(function_description):
  module = importlib.import_module(function_description['module'])
  func = getattr(module, function_description['name'])
  return func
