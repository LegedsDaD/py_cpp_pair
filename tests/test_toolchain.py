import os
import unittest
from unittest import mock

from py_cpp.toolchain import auto_install_enabled


class TestToolchain(unittest.TestCase):
    def test_auto_install_flag(self):
        with mock.patch.dict(os.environ, {"PY_CPP_AUTO_INSTALL_COMPILER": "1"}):
            self.assertTrue(auto_install_enabled())
        with mock.patch.dict(os.environ, {"PY_CPP_AUTO_INSTALL_COMPILER": "0"}):
            self.assertFalse(auto_install_enabled())


if __name__ == "__main__":
    unittest.main()

