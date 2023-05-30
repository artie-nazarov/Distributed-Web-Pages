from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import unittest


class TestWebUI(unittest.TestCase):

    def setUp(self):
        # Specify the path to chromedriver.exe
        PATH_TO_DRIVER = 'C:\\chromedriver.exe'
        s=Service(PATH_TO_DRIVER)
        self.browser = webdriver.Chrome(service=s)
        self.addCleanup(self.browser.quit)

    def testPageTitle(self):
        self.browser.get('http://localhost:8080')
        self.assertIn('Welcome to Decentralized Internet', self.browser.title)

if __name__ == '__main__':
    unittest.main(verbosity=2)
