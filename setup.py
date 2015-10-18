from distutils.core import setup, Extension

setup(name='cpp_extension', version='1.0', ext_modules=[Extension('cpp_extension', ['cpp_extension.cpp'])])