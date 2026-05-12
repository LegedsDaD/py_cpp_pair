import unittest

import py_cpp as pcp
from py_cpp.platform_utils import which


@unittest.skipUnless(which("g++") or which("clang++"), "No C++ compiler available on PATH")
class TestBasic(unittest.TestCase):
    def test_add_function(self):
        ns = {}
        code = """
int add(int a,int b){
    return a+b;
}
"""
        # Execute in an isolated globals dict to validate injection behavior.
        exec(
            "import py_cpp as pcp\npcp.cpp(r'''%s''')\nresult = add(5, 7)\n" % code,
            ns,
            ns,
        )
        self.assertEqual(ns["result"], 12)


if __name__ == "__main__":
    unittest.main()

