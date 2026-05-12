import unittest
from unittest import mock

import py_cpp as pcp
from py_cpp.errors import PyCppError


class TestInstaller(unittest.TestCase):
    def test_install_not_found_prints_message(self):
        with mock.patch("py_cpp.installer.find_vcpkg") as fv, mock.patch("py_cpp.installer.run") as rn:
            fv.return_value = mock.Mock(root=".", exe="vcpkg")
            rn.side_effect = PyCppError("failed")
            with mock.patch("builtins.print") as pr:
                ok = pcp.install("definitely-not-a-real-port")
                self.assertFalse(ok)
                pr.assert_called_with("Sorry, library not found.")


if __name__ == "__main__":
    unittest.main()

