import time
import os
import stat
import subprocess
import sys
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Optional # Added for type hinting

# Function to install dependencies in Colab
def install_dependencies():
    """Installs firefox and geckodriver for Selenium."""
    print("Installing Firefox and GeckoDriver...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
        subprocess.check_call(["apt-get", "update"])
        subprocess.check_call(["apt-get", "install", "-y", "firefox"])
        # Download and install geckodriver
        geckodriver_version = "v0.36.0" # Check for the latest version if needed
        geckodriver_url = f"https://github.com/mozilla/geckodriver/releases/download/{geckodriver_version}/geckodriver-{geckodriver_version}-linux64.tar.gz"
        subprocess.check_call(["wget", geckodriver_url])
        subprocess.check_call(["tar", "-xvzf", f"geckodriver-{geckodriver_version}-linux64.tar.gz"])
        # Make geckodriver executable
        st = os.stat("geckodriver")
        os.chmod("geckodriver", st.st_mode | stat.S_IEXEC)
        print("Installation complete.")
        return os.path.abspath("geckodriver") # Return the absolute path
    except subprocess.CalledProcessError as e:
        print(f"Error during dependency installation: {e}", file=sys.stderr)
        return None
    except FileNotFoundError as e:
         print(f"Error: 'wget' or 'tar' command not found. Please ensure they are installed. {e}", file=sys.stderr)
         return None

class Driver:
    def __init__(self, url, cookie=None):
        self.driver: Optional[webdriver.Firefox] = None # Initialize driver as None
        self.geckodriver_path: Optional[str] = None
        self.geckodriver_path = install_dependencies()
        # If installation failed in Colab, don't proceed
        if not self.geckodriver_path:
            print("Failed to set up GeckoDriver in Colab. Driver not initialized.", file=sys.stderr)
            return # Stop initialization

        self.driver = self._create_driver(url, cookie)

    def navigate(self, url, wait=3):
        if not self.driver:
            print("Driver not initialized.", file=sys.stderr)
            return
        try:
            self.driver.get(url)
            time.sleep(wait) # Consider using WebDriverWait for more robust waits
        except TimeoutException:
            print(f"Timeout occurred while navigating to {url}", file=sys.stderr)
        except WebDriverException as e:
            print(f"WebDriverException during navigation to {url}: {e}", file=sys.stderr)

    def scroll_to_bottom(self, wait=3):
        if not self.driver:
            print("Driver not initialized.", file=sys.stderr)
            return
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait)
        except WebDriverException as e:
            print(f"WebDriverException during scroll: {e}", file=sys.stderr)


    def get_element(self, selector) -> Optional[WebElement]:
        if not self.driver:
            print("Driver not initialized.", file=sys.stderr)
            return None
        try:
            return self.driver.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            print(f"Element not found with selector: {selector}", file=sys.stderr)
            return None
        except WebDriverException as e:
            print(f"WebDriverException finding element {selector}: {e}", file=sys.stderr)
            return None

    def get_elements(self, selector) -> List[WebElement]:
        if not self.driver:
            print("Driver not initialized.", file=sys.stderr)
            return []
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, selector)
        except WebDriverException as e:
            print(f"WebDriverException finding elements {selector}: {e}", file=sys.stderr)
            return [] # Return empty list on error

    def fill_text_field(self, selector, text):
        if not self.driver:
            print("Driver not initialized.", file=sys.stderr)
            return
        try:
            element = self.get_element(selector)
            if element:
                element.clear()
                element.send_keys(text)
            else:
                print(f"Cannot fill field, element not found: {selector}", file=sys.stderr)
        except WebDriverException as e:
            print(f"WebDriverException filling field {selector}: {e}", file=sys.stderr)


    def click_button(self, selector):
        if not self.driver:
            print("Driver not initialized.", file=sys.stderr)
            return
        try:
            element = self.get_element(selector)
            if element:
                element.click()
            else:
                 print(f"Cannot click button, element not found: {selector}", file=sys.stderr)
        except WebDriverException as e:
            # Catch issues like element is not clickable at point
            print(f"WebDriverException clicking button {selector}: {e}", file=sys.stderr)


    def _create_driver(self, url, cookie) -> Optional[webdriver.Firefox]:
        

        firefox_options = Options()
        # Uncomment the line below if you want to run in headless mode
        firefox_options.add_argument("--headless")

        # Setup WebDriver service
        service = Service(GeckoDriverManager().install())

        # Create WebDriver instance
        

        # service = None
        # if self.geckodriver_path:
        #      print("Assigning the service:({self.geckodriver_path})")
        #      service = FirefoxService(executable_path=self.geckodriver_path)

        driver = None
        try:
            print("Initializing Firefox WebDriver...")
            driver = webdriver.Firefox(service=service, options=firefox_options)
            print("WebDriver initialized. Navigating to initial URL...")
            driver.get(url) # Initial navigation
            print(f"Initial navigation to {url} complete.")
            if cookie:
                print("Adding cookie...")
                driver.add_cookie(cookie)
                print("Cookie added.")
                # Optionally navigate again after adding cookie if needed
                # driver.get(url)
                # print(f"Navigated to {url} again after adding cookie.")
            return driver
        except WebDriverException as e:
            print(f"Failed to create WebDriver or navigate initially: {e}", file=sys.stderr)
            if driver:
                driver.quit() # Try to clean up if partially created
            return None
        except Exception as e:
            # Catch any other unexpected error during setup
            print(f"Unexpected error during WebDriver creation: {e}", file=sys.stderr)
            if driver:
                driver.quit()
            return None

    def close(self):
        if self.driver:
            try:
                print("Closing WebDriver...")
                self.driver.quit() # Use quit() instead of close() for full cleanup
                self.driver = None # Mark driver as closed
                print("WebDriver closed.")
            except WebDriverException as e:
                print(f"Error closing WebDriver: {e}", file=sys.stderr)
        else:
             print("Attempted to close WebDriver, but it was not initialized or already closed.")