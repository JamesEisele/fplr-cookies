#!/usr/bin/env python3
'''
This script is meant to serve as a basic proof of concept for bypassing FPL
Review's login CAPTCHA by using pre-generated sessions.
'''
import json
import sys
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pathlib
import os

def main( ):

    total_session_count = input('How many sessions do you want to generate? [1]: ')
    if total_session_count == '':
        total_session_count = 1
    else:
        total_session_count = int(total_session_count)

    with open('fplr_credentials.json') as fplr_creds_file:
        fplr_creds = json.load(fplr_creds_file)

    scriptDirectory = pathlib.Path().absolute()

    # Create number of sessions specified in 'total_session_count'.
    for session in range(total_session_count):
        # Create unique session name for each session data directory (ISO 8601).
        # Note: Selenium doesn't like colons or hyphens in the 'user-data-dir' arg.
        session_name = (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-sessiondata')

        # Specify Selenium options (Windows OS example).
        chrome_options = Options()
        chrome_options.add_argument(f'user-data-dir={scriptDirectory}\\sessions\\{session_name}')
        driver = webdriver.Chrome(
            executable_path=r'C:\\WebDriver\\bin\\chromedriver.exe',
            options=chrome_options)

        base_URL = r'https://fplreview.com/'
        driver = fplr_login(base_URL + 'fplr_enter/', driver, fplr_creds)

        # Find expiration date of the session login cookie.
        session_cookies = driver.get_cookies()
        for cookie in session_cookies:
            if cookie['name'][:19] == 'wordpress_logged_in':   # Only cookie we care about.
                final_session_name = datetime.utcfromtimestamp(cookie["expiry"]).strftime('%Y%m%dT%H%M%SZ') + '-sessiondata'
                break
        
        driver.quit()

        # Rename the session data folder to reflect the expiration date.
        try:
            initial_data_directory = f'{scriptDirectory}\\sessions\\{session_name}'  # current working directory
            final_data_directory = f'{scriptDirectory}\\sessions\\{final_session_name}'
            os.rename(initial_data_directory, final_data_directory)
        except:
            print('Failed to rename session data directory to reflect expiration date.')

        # TODO: Add cleanup for session data files that are leftover from broken sessions/testing.

    sys.exit(0)

def fplr_login(login_URL, driver, fplr_creds):
    '''
    Login to FPL Review site, allow user to manually complete CAPTCHA,
    proceed with login.
    '''

    driver.get(login_URL)
    driver.find_element(By.XPATH, '//input[@data-key="username"]').send_keys(fplr_creds['email'])
    driver.find_element(By.XPATH, '//input[@data-key="user_password"]').send_keys(fplr_creds['password'])
    driver.find_element(By.CSS_SELECTOR, ".um-icon-android-checkbox-outline-blank").click() # "Keep me singed in"

    # Note: CAPTCHA elements are loaded via iframes so they need to be read separately.
    time.sleep(3) # Wait for iframe to load.
    driver.switch_to.frame(driver.find_element(By.XPATH, '//iframe[@title="reCAPTCHA"]'))

    # Wait for user input to complete CAPTCHA, continue after success.
    done = False
    timer = 0 
    while not done:
        time.sleep(1)
        timer += 1

        # Monitor CAPTCHA status.
        element = driver.find_element(By.CLASS_NAME, 'rc-anchor-aria-status')
        if str(element.get_attribute('innerText')) == 'You are verified':
            driver.switch_to.default_content()
            driver.find_element(By.ID, 'um-submit-btn').click() # Login button
            done = True

        elif timer == 180:
            print('Failed to complete CAPTCHA after 180 seconds. Stopping...')
            driver.quit()
            sys.exit(0)

    return driver

if __name__ == '__main__':
   main()
