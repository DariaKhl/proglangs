This repository contains task №1 - **C++ module for Python**

### Build

To build `.so` C++ library use
```bash
python3.4 setup.py build
```

Once the library is build, copy `cpp_extension.cpython-34m.so` from `build/lib.linux-i686-3.4/` to root of project directory (on the same level with `python_core.py`)

### Launch

To run the program use:
```bash
python3.4 python_core.py <input_file> <output_file>
```
where:
* `<input_file>` - path to XML-file which contains description of electrical circuit.
* `<output_file>` - path to file, where program's output should be provided.

