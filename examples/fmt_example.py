import py_cpp as pcp

pcp.install("fmt")

pcp.cpp(
    r"""
#include <fmt/core.h>
#include <string>

std::string hello(std::string name){
    return fmt::format("Hello, {}!", name);
}
"""
)

print(hello("world"))

