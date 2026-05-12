#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// ---- User code ----
{{USER_CODE}}

// ---- Pybind11 bindings (auto-generated) ----
PYBIND11_MODULE({{MODULE_NAME}}, m) {
{{BINDINGS}}
}

