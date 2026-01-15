# CTool

A CMake wrapper and toolset.

## Commands

- `ctool-build` - wrapper around `cmake --build`
- `ctool-configure` - wrapper around `cmake` that refuses to perform an in-tree build
- `ctool-package` - wrapper around `cpack`
- `ctool-test` - wrapper around `ctest`

`ctool-build` and `ctool-configure` will not perform an in-tree build.
When run within a source tree, will create a binary directory, `build` by default, and change to it before calling the wrapper tool.

## Planned tools

- `ctool-depends` - detect missing dependencies and install them using distribution package managers
- `ctool-changed-tests` - use cmake-file-api and CTest json to determine what files might change the output of which tests
