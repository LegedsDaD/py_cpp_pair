from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class CppFunction:
    name: str


@dataclass(frozen=True)
class CppField:
    name: str


@dataclass(frozen=True)
class CppMethod:
    name: str


@dataclass(frozen=True)
class CppClass:
    name: str
    fields: list[CppField] = field(default_factory=list)
    methods: list[CppMethod] = field(default_factory=list)
    has_default_ctor: bool = True


@dataclass(frozen=True)
class ParseResult:
    functions: list[CppFunction]
    classes: list[CppClass]


_re_comment_sl = re.compile(r"//.*?$", re.M)
_re_comment_ml = re.compile(r"/\\*.*?\\*/", re.S)


def _strip_comments(code: str) -> str:
    code = _re_comment_ml.sub("", code)
    code = _re_comment_sl.sub("", code)
    return code


def parse_cpp(code: str) -> ParseResult:
    """
    MVP regex parser:
    - Free functions with bodies: `ret name(args){...}`
    - Classes: `class Name { ... };` and only `public:` section members
    """
    src = _strip_comments(code)

    classes: list[CppClass] = []

    # Very naive class capture (no nested classes)
    for m in re.finditer(r"\bclass\s+([A-Za-z_]\w*)\s*\{(.*?)\}\s*;", src, re.S):
        name = m.group(1)
        body = m.group(2)

        public_body = body
        pub = re.search(r"\bpublic\s*:\s*(.*)", body, re.S)
        if pub:
            public_body = pub.group(1)
            # stop at protected/private if present
            stop = re.search(r"\b(private|protected)\s*:\s*", public_body)
            if stop:
                public_body = public_body[: stop.start()]

        fields: list[CppField] = []
        methods: list[CppMethod] = []

        # Fields: `type name;` or `type name = ...;`
        for fm in re.finditer(r"\b[A-Za-z_]\w*(?:\s+[*&])?\s+([A-Za-z_]\w*)\s*(?:=[^;]*)?;", public_body):
            fields.append(CppField(name=fm.group(1)))

        # Methods: `ret name(args){` and constructors `Name(...){`
        for mm in re.finditer(r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{", public_body):
            meth = mm.group(1)
            if meth == name:
                continue
            methods.append(CppMethod(name=meth))

        classes.append(CppClass(name=name, fields=_dedupe_fields(fields), methods=_dedupe_methods(methods)))

    # Remove class bodies before scanning for free functions (avoid picking up methods)
    src_wo_classes = re.sub(r"\bclass\s+[A-Za-z_]\w*\s*\{.*?\}\s*;", "", src, flags=re.S)

    functions: list[CppFunction] = []
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{", src_wo_classes):
        name = m.group(1)
        # ignore control keywords
        if name in {"if", "for", "while", "switch", "catch"}:
            continue
        functions.append(CppFunction(name=name))

    return ParseResult(functions=_dedupe_functions(functions), classes=_dedupe_classes(classes))


def _dedupe_functions(items: list[CppFunction]) -> list[CppFunction]:
    seen: set[str] = set()
    out: list[CppFunction] = []
    for it in items:
        if it.name in seen:
            continue
        seen.add(it.name)
        out.append(it)
    return out


def _dedupe_classes(items: list[CppClass]) -> list[CppClass]:
    seen: set[str] = set()
    out: list[CppClass] = []
    for it in items:
        if it.name in seen:
            continue
        seen.add(it.name)
        out.append(it)
    return out


def _dedupe_fields(items: list[CppField]) -> list[CppField]:
    seen: set[str] = set()
    out: list[CppField] = []
    for it in items:
        if it.name in seen:
            continue
        seen.add(it.name)
        out.append(it)
    return out


def _dedupe_methods(items: list[CppMethod]) -> list[CppMethod]:
    seen: set[str] = set()
    out: list[CppMethod] = []
    for it in items:
        if it.name in seen:
            continue
        seen.add(it.name)
        out.append(it)
    return out

