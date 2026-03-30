import unittest
import sys
import os
import importlib
import importlib.util

PLUGIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PLUGIN_NAME = os.path.basename(PLUGIN_DIR)

sys.path.insert(0, os.path.dirname(PLUGIN_DIR))


def load_plugin_as_package():
    """Ładuje plugin jako pakiet (naprawia relative imports)"""
    spec = importlib.util.spec_from_file_location(
        PLUGIN_NAME,
        os.path.join(PLUGIN_DIR, '__init__.py'),
        submodule_search_locations=[PLUGIN_DIR]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[PLUGIN_NAME] = module
    spec.loader.exec_module(module)
    return module


class TestPluginComponents(unittest.TestCase):
    """Sprawdza czy komponenty wtyczki działają poprawnie"""

    @classmethod
    def setUpClass(cls):
        cls.plugin = load_plugin_as_package()

    def test_plugin_imports(self):
        self.assertIsNotNone(self.plugin)

    def test_constants_defined(self):
        self.assertTrue(hasattr(self.plugin, 'PLUGIN_NAME'), "Brak stałej PLUGIN_NAME")
        self.assertTrue(hasattr(self.plugin, 'PLUGIN_VERSION'), "Brak stałej PLUGIN_VERSION")
        self.assertIsInstance(self.plugin.PLUGIN_NAME, str)
        self.assertIsInstance(self.plugin.PLUGIN_VERSION, str)
        self.assertGreater(len(self.plugin.PLUGIN_NAME), 0)

    def test_translation_utils(self):
        utils = importlib.import_module(f"{PLUGIN_NAME}.utils")
        result = utils.TranslationUtils.tr("Test")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_message_utils_exists(self):
        utils = importlib.import_module(f"{PLUGIN_NAME}.utils")
        self.assertTrue(hasattr(utils, 'MessageUtils'))

    def test_version_format(self):
        import re
        pattern = re.compile(r'^\d+\.\d+\.\d+$')
        self.assertRegex(
            self.plugin.PLUGIN_VERSION,
            pattern,
            f"PLUGIN_VERSION '{self.plugin.PLUGIN_VERSION}' nie jest w formacie X.Y.Z"
        )


if __name__ == '__main__':
    unittest.main()