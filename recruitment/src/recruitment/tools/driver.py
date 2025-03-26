import time
import os
import stat
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

# Function to install dependencies in Colab
def install_dependencies():
    """Installs firefox and geckodriver for Selenium."""
    print("Installing Firefox and GeckoDriver...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    subprocess.check_call(["apt-get", "update"])
    subprocess.check_call(["apt-get", "install", "-y", "firefox"])
    # Download and install geckodriver
    geckodriver_version = "v0.34.0" # Check for the latest version if needed
    geckodriver_url = f"https://github.com/mozilla/geckodriver/releases/download/{geckodriver_version}/geckodriver-{geckodriver_version}-linux64.tar.gz"
    subprocess.check_call(["wget", geckodriver_url])
    subprocess.check_call(["tar", "-xvzf", f"geckodriver-{geckodriver_version}-linux64.tar.gz"])
    # Make geckodriver executable
    st = os.stat("geckodriver")
    os.chmod("geckodriver", st.st_mode | stat.S_IEXEC)
    print("Installation complete.")
    return os.path.abspath("geckodriver") # Return the absolute path

class Driver:
    def __init__(self, url, cookie=None):
        # --- Added for Colab ---
        # Check if running in Colab and install dependencies if necessary
        self.geckodriver_path = None
        if 'google.colab' in sys.modules:
             self.geckodriver_path = install_dependencies()
        # -----------------------
        self.driver = self._create_driver(url, cookie)


    def navigate(self, url, wait=3):
        self.driver.get(url)
        time.sleep(wait)

    def scroll_to_bottom(self, wait=3):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(wait)

    def get_element(self, selector):
        return self.driver.find_element(By.CSS_SELECTOR, selector)

    def get_elements(self, selector):
        return self.driver.find_elements(By.CSS_SELECTOR, selector)

    def fill_text_field(self, selector, text):
        element = self.get_element(selector)
        element.clear()
        element.send_keys(text)

    def click_button(self, selector):
        element = self.get_element(selector)
        element.click()

    def _create_driver(self, url, cookie):
        options = Options()
        options.add_argument("--headless") # Run headless to avoid display issues in Colab
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # --- Modified for Colab ---
        service = None
        if self.geckodriver_path:
             service = FirefoxService(executable_path=self.geckodriver_path)
        # If not in Colab or geckodriver_path is None, Selenium might find it if it's in PATH
        driver = webdriver.Firefox(options=options, service=service)
        # --------------------------

        driver.get(url)
        if cookie:
            driver.add_cookie(cookie)
        return driver

    def close(self):
        self.driver.close()
