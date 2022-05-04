import sys
from unittest import TestCase


class InstallationTests(TestCase):

    def test_console_entrypoint(self):
        from core.cli import entry
        sys.argv = []
        assert entry() is True