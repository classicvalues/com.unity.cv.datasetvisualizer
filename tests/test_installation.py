from unittest import TestCase, main as test_runner


class InstallationTests(TestCase):

    def test_console_entrypoint(self):
        print(help('modules'))

        from unity_cv_datasetvisualizer.core.cli import entry
        entry()


if __name__ == '__main__':
    test_runner()
