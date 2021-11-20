#!/usr/bin/env python3
'''
This import script allows users to import existing Chromium sessions with
Selenium so that you can bypass CAPTCHAs when running automated scripts.
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pathlib
import sys

def main( ):

    # Set path for session data directory.
    scriptDirectory = pathlib.Path().absolute()

    # Get list of all saved sessions from '\sessions' folder.
    sessions_path = pathlib.Path(r'.\\sessions').absolute()
    session_list = [x for x in sessions_path.iterdir() if x.is_dir()]

    print('Existing sessions found:')
    for session in session_list:
        print(f' - {session}')
    print('\n')
    print('-'*80)

    for session in session_list:
        print(f'CHECKING SESSION: {session}')
        # Specify Selenium options (Windows OS example).
        chrome_options = Options()
        #chrome_options.add_argument(f'user-data-dir={scriptDirectory}\\userdata')
        chrome_options.add_argument(f'user-data-dir={session}')
        driver = webdriver.Chrome(
            executable_path=r'C:\\WebDriver\\bin\\chromedriver.exe',
            options=chrome_options
        )

        base_URL = 'https://fplreview.com/'

        # (OPTIONAL) Manually verify that page is authenticated.
        driver.get(f'{base_URL}account/') 
        time.sleep(1)

        # Print cookies & corresponding expiration dates
        # TODO: Remove session data folder if session is expired by checking
        # directory name against current UTC time.
        session_cookies = driver.get_cookies()
        for cookie in session_cookies:
            if cookie['name'][:19] == 'wordpress_logged_in':   # Only cookie we care about.
                print('Expires:', time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(cookie['expiry'])))
            else:
                print(cookie['name'][:19])

        driver.quit()

    sys.exit(0)

if __name__ == '__main__':
   main()
