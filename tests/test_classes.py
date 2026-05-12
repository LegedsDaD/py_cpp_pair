import unittest

import py_cpp as pcp
from py_cpp.platform_utils import which


@unittest.skipUnless(which("g++") or which("clang++"), "No C++ compiler available on PATH")
class TestClasses(unittest.TestCase):
    def test_robot_class(self):
        pcp.cpp(
            r"""
class Robot {
public:
    int power = 100;
    Robot() {}
    int attack(){ return power * 2; }
};
"""
        )
        r = Robot()
        self.assertEqual(r.attack(), 200)


if __name__ == "__main__":
    unittest.main()

