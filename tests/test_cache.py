import os
import time
import unittest

import py_cpp as pcp
from py_cpp.cache import get_entry
from py_cpp.platform_utils import which


@unittest.skipUnless(which("g++") or which("clang++"), "No C++ compiler available on PATH")
class TestCache(unittest.TestCase):
    def test_reuses_build_output(self):
        code = "int add(int a,int b){ return a+b; }"
        entry = get_entry(code)
        if entry.pyd_path.exists():
            os.remove(entry.pyd_path)

        pcp.cpp(code)
        self.assertTrue(entry.pyd_path.exists())
        t1 = entry.pyd_path.stat().st_mtime

        time.sleep(0.5)
        pcp.cpp(code)
        t2 = entry.pyd_path.stat().st_mtime

        self.assertEqual(t1, t2)


if __name__ == "__main__":
    unittest.main()

