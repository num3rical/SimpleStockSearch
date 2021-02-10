import sys
from os import path
from json import (load as jsonload, dump as jsondump)

SITE_KEYS = ['-TRADINGVIEW-', '-TWITTER-', '-YAHOOFINANCE-', '-MARKETWATCH-', '-SEEKINGALPHA-', '-STOCKCHARTS-', '-OPENINSIDER-', '-FINVIZ-', '-ROBINHOOD-']
SETTINGS_FILE = path.join(path.dirname(sys.executable), r'config.cfg')
DEFAULT_SETTINGS = {'theme': 'SSSDefault', 'enabled_sites_keys': ['-TRADINGVIEW-', '-TWITTER-', '-YAHOOFINANCE-']}
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'theme': '-THEME-'}
print(SETTINGS_FILE)
def load_settings(settings_file, default_settings):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        settings = default_settings
        save_settings(settings_file, settings, None)
    return settings

def save_settings(settings_file, settings, values):
    if values:
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'Problem updating settings from window values. Key = {key}')

        for key in values:
            if key in SITE_KEYS:
                if values[key] == True:
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
