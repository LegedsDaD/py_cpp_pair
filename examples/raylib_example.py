import py_cpp as pcp

# Note: raylib may require platform-specific graphics dependencies.
pcp.install("raylib")

pcp.cpp(
    r"""
#include <raylib.h>

int raylib_version_major(){
    return RAYLIB_VERSION_MAJOR;
}
"""
)

print(raylib_version_major())

