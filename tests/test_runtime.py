import unittest

import py_cpp as pcp
from py_cpp.platform_utils import which


@unittest.skipUnless(which("g++") or which("clang++"), "No C++ compiler available on PATH")
class TestRuntime(unittest.TestCase):
    def test_cpp_returns_module(self):
        mod = pcp.cpp("int add(int a,int b){ return a+b; }")
        self.assertTrue(hasattr(mod, "add"))

    def test_version(self):
        self.assertEqual(pcp.version(), "1.0.0")


if __name__ == "__main__":
    unittest.main()

