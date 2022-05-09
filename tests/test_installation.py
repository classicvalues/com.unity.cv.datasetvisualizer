import sys
from unittest import TestCase


class InstallationTests(TestCase):
    def test_console_entrypoint(self):
        from datasetvisualizer.core.cli import entry

        sys.argv = []
        assert entry() is True
