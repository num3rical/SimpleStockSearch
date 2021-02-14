import sys
from os import path
from json import (load as jsonload, dump as jsondump)

SETTINGS_FILE = path.join(path.dirname(sys.executable), r'config.cfg')

SITE_KEYS = [
    '-TRADINGVIEW-',
    '-TWITTER-',
    '-YAHOOFINANCE-',
    '-MARKETWATCH-',
    '-SEEKINGALPHA-',
    '-STOCKCHARTS-',
    '-OPENINSIDER-',
    '-FINVIZ-',
    '-ROBINHOOD-'
]

DEFAULT_SETTINGS = {
    'theme': 'SSSDefault',
    'enabled_sites_keys': ['-TRADINGVIEW-', '-TWITTER-', '-YAHOOFINANCE-']
}

SETTINGS_KEYS_TO_ELEMENT_KEYS = {
    'theme': '-THEME-'
}


# load_settings: Reads the settings file, sets the contents equal to the
# 'settings' variable, and returns it.
def load_settings(settings_file, default_settings):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    # If the settings file cannot be found, creates one with default settings.
    except Exception as e:
        settings = default_settings
        save_settings(settings_file, settings, None)
    return settings


# save_settings: Gets the value of each setting from the 'settings' variable,
# adds each enabled website to 'enabled_sites_keys', and saves to the settings
# file.
def save_settings(settings_file, settings, values):
    if values:
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'Problem updating settings from window values. Key = {key}')

        for key in values:
            if key in SITE_KEYS:
                if values[key]:
                    if key not in settings['enabled_sites_keys']:
                        try:
                            settings['enabled_sites_keys'].append(key)
                            print(settings)
                        except Exception as e:
                            print(e)
                            print(f'Problem updating settings from window values. Key = {key}')
                else:
                    if key in settings['enabled_sites_keys']:
                        try:
                            settings['enabled_sites_keys'].remove(key)
                        except Exception as e:
                            print(e)
                            print(f'Problem updating settings from window values. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)
