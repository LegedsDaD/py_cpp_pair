from __future__ import annotations

import importlib.resources as resources
from dataclasses import dataclass

from .parser import ParseResult


@dataclass(frozen=True)
class WrapperResult:
    module_name: str
    source: str


def generate_wrapper(*, user_code: str, parse: ParseResult, module_name: str) -> WrapperResult:
    bindings: list[str] = []
    for fn in parse.functions:
        bindings.append(f'    m.def("{fn.name}", &{fn.name});')

    for cls in parse.classes:
        bindings.append(f'    py::class_<{cls.name}>(m, "{cls.name}")')
        bindings.append("        .def(py::init<>())")
        for meth in cls.methods:
            bindings.append(f'        .def("{meth.name}", &{cls.name}::{meth.name})')
        for field in cls.fields:
            bindings.append(f'        .def_readwrite("{field.name}", &{cls.name}::{field.name})')
        bindings.append("        ;")

    template = resources.files("py_cpp.templates").joinpath("wrapper_template.cpp").read_text(encoding="utf-8")
    source = (
        template.replace("{{MODULE_NAME}}", module_name)
        .replace("{{USER_CODE}}", user_code.rstrip())
        .replace("{{BINDINGS}}", "\n".join(bindings))
    )
    return WrapperResult(module_name=module_name, source=source)
