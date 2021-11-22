#!/usr/bin/env python3
'''
This import script allows users to import existing Chromium sessions with
Selenium so that you can bypass CAPTCHAs when running automated scripts.
'''

from datetime import datetime, timezone, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import pathlib
import sys
import shutil

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

    # Get current UTC time to compare against. Accuracy here isn't that
    # necessary so we just stick to calling it once at runtime.
    current_UTC = datetime.utcnow() # Naive datetime obj is preferable here.

    for session in session_list:
        print('-'*80)
        print(f'\nCHECKING SESSION: {session}')
     
        # Create datetime object from session data directory name.
        timestamp_str = session.name
        timestamp_str = timestamp_str[:-12] # Remove trailing "session-data".
        timestamp_obj = datetime.strptime(timestamp_str, '%Y%m%dT%H%M%SZ')

        # Check dir UTC timestamp agaisnt UTC time now, delete expired sessions.
        if current_UTC > timestamp_obj:
            print(' > Session data is expired! Deleting directory...')
            try:
                shutil.rmtree(session)
                continue
            except:
                print(' > Failed to delete session data directory! ')
        else:
            print(' > Session data is still good.')

        # Specify Selenium options (Windows OS example).
        chrome_options = Options()
        chrome_options.add_argument(f'user-data-dir={session}')
        chrome_service = Service(r'C:\\WebDriver\\bin\\chromedriver.exe')
        driver = webdriver.Chrome(
            service=chrome_service,
            options=chrome_options)

        base_URL = 'https://fplreview.com/'

        # (OPTIONAL) Manually verify that page is authenticated.
        driver.get(f'{base_URL}account/') 
        time.sleep(1)
        # Print cookies & corresponding expiration dates in your local timezone.
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
