import PySimpleGUIQt as sg
import webbrowser as web
import requests
from pynput import keyboard
import settings as usersettings

hotkeyActivated = False

# This theme is actually the DarkGrey11 theme from PySimpleGUI, except with 0
# border width. For some reason, PySimpleGUIQt doesn't have this theme so I
# had to recreate it and name it SSSDefault.
sg.LOOK_AND_FEEL_TABLE['SSSDefault'] = {
    "BACKGROUND": "#1c1e23",
    "TEXT": "#cccdcf",
    "INPUT": "#313641",
    "TEXT_INPUT": "#cccdcf",
    "SCROLL": "#313641",
    "BUTTON": ("#f5f5f6", "#313641"),
    "PROGRESS": ('#01826B', '#D0D0D0'),
    "BORDER": 0,
    "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0,
}

# The menu structure for the SystemTray
trayMenu = ['BLANK', ['&Open', 'Exit']]


# getExchangeName: Makes a request to Yahoo Finance in order to get the name
# of the exchange the specified stock is a part of, uses exchangeNamesDict to
# convert to the name that is compatible with TradingView, and returns the
# exchange name as a string.
def getExchangeName(symbol):

    exchangeNamesDict = {
        'NasdaqGS': 'NASDAQ',
        'NYSE': 'NYSE'
    }

    try:
        resp = requests.get(f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=price")
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    resp = resp.json()

    try:
        exchange = resp['quoteSummary']['result'][0]['price']['exchangeName']
    except Exception:
        return False

    try:
        exchange = exchangeNamesDict[exchange]
    except Exception as e:
        print(e)
        return False

    return exchange


# openSites: Runs through a list of keys in the enabled sites from the user's
# settings, gets the URL for each of those keys by using the dictionary
# keys_to_urls, and opens the URLs in a new browser tab.
def openSites(settings, exchangeName, symbol):

    keys_to_urls = {
        '-TRADINGVIEW-': f'https://www.tradingview.com/chart/?symbol={exchangeName}%3A{symbol}',
        '-TWITTER-': f'https://twitter.com/search?q=%24{symbol}',
        '-YAHOOFINANCE-': f'https://finance.yahoo.com/quote/{symbol}',
        '-MARKETWATCH-': f'https://www.marketwatch.com/investing/stock/{symbol}',
        '-SEEKINGALPHA-': f'https://seekingalpha.com/symbol/{symbol}',
        '-STOCKCHARTS-': f'https://stockcharts.com/h-sc/ui?s={symbol}',
        '-OPENINSIDER-': f'http://openinsider.com/{symbol}',
        '-FINVIZ-': f'https://finviz.com/quote.ashx?t={symbol}',
        '-ROBINHOOD-': f'https://robinhood.com/stocks/{symbol}',
    }

    for key in range(len(settings['enabled_sites_keys'])):
        key = keys_to_urls[settings['enabled_sites_keys'][key]]
        web.open_new_tab(key)


# createMainWindow: Creates and returns the main program window with the
# specified user settings.
def createMainWindow(settings):

    sg.theme(settings['theme'])
    sg.theme_border_width(0)
    layout = [
        [
            sg.Text('$', key='-TEXT-', font=("any", 30), pad=(0, 0), enable_events=True, tooltip='Click to open settings'),
            sg.InputText(key='-SYMBOL-', background_color=sg.theme_background_color(), focus=True, enable_events=True, font=("any", 30), pad=(0, 0), size=(15, 2))
        ],
        [sg.Button('Submit', visible=False, bind_return_key=True)]
    ]

    window = sg.Window('SimpleStockSearch', layout, no_titlebar=True, grab_anywhere=True, keep_on_top=True, return_keyboard_events=True, finalize=True)

    return window


# createSettingsWindow: Creates and returns the settings window with the specified user settings.
def createSettingsWindow(settings):

    sg.theme(settings['theme'])
    sg.theme_border_width(0)
    layout = [
        [
            sg.Text('Theme'),
            sg.Combo(sg.theme_list(), key='-THEME-', default_value='SSSDefault')
        ],
        [sg.Text(' ')],
        [sg.Frame(
            layout=[
                [
                    sg.Checkbox('TradingView', key='-TRADINGVIEW-'),
                    sg.Checkbox('Yahoo Finance', key='-YAHOOFINANCE-')
                ],
                [
                    sg.Checkbox('Twitter', key='-TWITTER-'),
                    sg.Checkbox('MarketWatch', key='-MARKETWATCH-')
                ],
                [
                    sg.Checkbox('Seeking Alpha', key='-SEEKINGALPHA-'),
                    sg.Checkbox('StockCharts', key='-STOCKCHARTS-')
                ],
                [
                    sg.Checkbox('OpenInsider', key='-OPENINSIDER-'),
                    sg.Checkbox('FINVIZ', key='-FINVIZ-')
                ],
                [
                    sg.Checkbox('Robinhood', key='-ROBINHOOD-')
                ]
            ],
            title='Websites'
        )],
        [sg.Text(' ')],
        [sg.Button('Cancel'), sg.Button('Save')]
    ]

    window = sg.Window('Settings', layout, keep_on_top=True, resizable=False, disable_minimize=True, font=('Any', 11), finalize=True)

    # Updates the settings shown as selected from the users settings.
    for key in usersettings.SETTINGS_KEYS_TO_ELEMENT_KEYS:
        try:
            window[usersettings.SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

    # Checks the Checkboxes in the window if their respected values are found in the user's enabled_sites_keys.
    for i in range(len(settings['enabled_sites_keys'])):
        try:
            window[settings['enabled_sites_keys'][i]].update(value=True)
        except Exception as e:
            print(e)
            print(f'Problem updating PySimpleGUI window from settings. Key = {settings["enabled_sites_keys"][i]}')

    return window


# main: Loads the user settings, creates and reads the windows/system tray,
# and handles the hotkeys.
def main():

    settings = usersettings.load_settings(usersettings.SETTINGS_FILE, usersettings.DEFAULT_SETTINGS)

    window = createMainWindow(settings)

    # This is necessary to focus the window once created because of a bug that
    # doesn't do it automatically.
    # See https://github.com/PySimpleGUI/PySimpleGUI/issues/3877.
    window.QTWindow.activateWindow()

    # TODO: Find a way to not use a global variable for determining the hotkey
    # is activated. This is used to stop the tray from reading and I'm not
    # actually sure there is another way to do it.
    global hotkeyActivated

    # Basically the main loop of the program, which reads from the main and
    # settings windows. Once closed, the SystemTray is created and a new loop
    # begins.
    while True:
        event, values = window.read()

        if event == 'Submit':
            symbol = values['-SYMBOL-']
            exchangeName = getExchangeName(symbol)

            if exchangeName is False:
                sg.popup(f'There was an error retrieving data for ticker symbol: {symbol}', keep_on_top=True)
                window['-SYMBOL-'].update('')
            else:
                openSites(settings, exchangeName, symbol)
                window['-SYMBOL-'].update('')
                break

        if event == '-TEXT-':
            event, values = createSettingsWindow(settings).read(close=True)

            if event == 'Save':
                usersettings.save_settings(usersettings.SETTINGS_FILE, settings, values)
                window.close()
                window = createMainWindow(settings)
                window.QTWindow.activateWindow()
            if event == 'Cancel' or event == sg.WIN_CLOSED:
                window.close()
                window = createMainWindow(settings)
                window.QTWindow.activateWindow()

        if event == '-SYMBOL-' and values['-SYMBOL-']:

            if len(values['-SYMBOL-']) > 5:
                window['-SYMBOL-'].update(values['-SYMBOL-'][:-1])
            else:
                window['-SYMBOL-'].update(values['-SYMBOL-'].upper())

        if event == "special 16777216":  # Esc
            break

    tray = sg.SystemTray(menu=trayMenu, data_base64=sg.DEFAULT_BASE64_ICON, tooltip='SimpleStockSearch')

    # Once the hotkey is activated, the global variable hotkeyActivated is set
    # to True, which closes the tray and restarts the main loop.
    def on_activate():

        global hotkeyActivated
        hotkeyActivated = True

    hotkeys = keyboard.GlobalHotKeys({
        '<shift>+<caps_lock>+4': on_activate})

    hotkeys.start()

    while True:
        window.close()
        menu_item = tray.read(timeout=500)

        if menu_item == 'Exit':
            break

        if hotkeyActivated or menu_item == 'Open':
            tray.close()

            hotkeyActivated = False

            main()
            break

    tray.close()


if __name__ == '__main__':
    main()
