DEFAULT_MAX_QGIS_VERSION = '4.99'
DEFAULT_MIN_QGIS_VERSION = '3.28'
DEFAULT_PLUGIN_VERSION = '0.1.0'
DEFAULT_AUTHOR = 'EnviroSolutions sp. z o. o.'
DEFAULT_EMAIL = 'office@envirosolutions.pl'
DEFAULT_TRACKER_URL = 'https://github.com/envirosolutions/'
DEFAULT_ISSUES_ENDPOINT = '/issues'

# enviro files and folders 
'''
if default then folder is main plugin folder
folderX means plugin_folder/folderX
{
    file1: folder1,
    file2: folder2,
}
'''
ENVIRO_FILES={
    'utils.py': 'default',
    'constants.py': 'default',
    'qgis_feed.py': 'default',
    'qgis_feed.ui': 'ui',
    'resources.py': 'default',
    '__init__.py': 'modules'
}

ENVIRO_FOLDERS=[
    'modules',
    'images',
    'ui'
]

DEFAULT_ENCODING = 'utf-8'

QT_VER = {
    6: "6."
}

INDUSTRIES = {
    "999": "Nie wybrano",
    "e": "Energetyka/OZE",
    "u": "Urząd",
    "td": "Transport/Drogi",
    "pg": "Planowanie/Geodezja",
    "wk": "WodKan",
    "s": "Środowisko",
    "rl": "Rolnictwo/Leśnictwo",
    "tk": "Telkom",
    "edu": "Edukacja",
    "i": "Inne",
    "it": "IT",
    "n": "Nieruchomości"
}
