import os
import configparser
import unittest

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), '..')


class TestPluginStructure(unittest.TestCase):
    """Sprawdza czy wymagane pliki i zasoby istnieją"""

    def test_metadata_exists(self):
        path = os.path.join(PLUGIN_DIR, 'metadata.txt')
        self.assertTrue(os.path.exists(path), "Brak pliku metadata.txt")

    def test_metadata_required_fields(self):
        path = os.path.join(PLUGIN_DIR, 'metadata.txt')
        config = configparser.ConfigParser()
        config.read(path)
        self.assertIn('general', config)
        for field in ['name', 'version', 'qgisMinimumVersion']:
            self.assertIn(field, config['general'], f"Brak pola '{field}' w metadata.txt")

    def test_icon_exists(self):
        path = os.path.join(PLUGIN_DIR, 'images', 'icon.png')
        self.assertTrue(os.path.exists(path), "Brak ikony images/icon.png")

    def test_ui_file_exists(self):
        ui_dir = os.path.join(PLUGIN_DIR, 'ui')
        self.assertTrue(os.path.exists(ui_dir), "Brak folderu ui/")
        ui_files = [f for f in os.listdir(ui_dir) if f.endswith('.ui')]
        self.assertGreater(len(ui_files), 0, "Brak plików .ui w folderze ui/")

    def test_i18n_folder_exists(self):
        path = os.path.join(PLUGIN_DIR, 'i18n')
        self.assertTrue(os.path.exists(path), "Brak folderu i18n/")


if __name__ == '__main__':
    unittest.main()