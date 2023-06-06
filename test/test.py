from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoAlertPresentException
import unittest
import src.data_storage as DS


class TestWebUI(unittest.TestCase):

    def setUp(self):
        # Specify the path to chromedriver.exe
        PATH_TO_DRIVER = 'C:\\chromedriver.exe'
        s=Service(PATH_TO_DRIVER)
        self.browser = webdriver.Chrome(service=s)
        self.addCleanup(self.browser.quit)

    def testCreateNetwork(self):
        self.browser.get('http://localhost:8080')
        self.assertIn('Welcome to Decentralized Internet', self.browser.title)
        create_button = self.browser.find_element('xpath','//button[@type="submit" and text()="Create"]')
        create_button.click()
        try:
            alert = self.browser.switch_to.alert
            alert_text = alert.text
            alert.accept()
        except NoAlertPresentException:
            self.fail("No alert present after clicking 'create' button.")
        else:
            expected_alert_text = 'Successfully created network'
            self.assertEqual(alert_text, expected_alert_text)

    def binary_data_partitioning_test():
        s = DS.DataStorage()
        data = b'123456789101werhuo425h43lhj5654nbvghk36lh43jghj1121314151617181920'
        m = s.prepare_data_partitions(data, 5)
        data_comp = s.compose_data_from_partitions(m.values())
        assert data == data_comp
        
if __name__ == '__main__':
    unittest.main(verbosity=1)
