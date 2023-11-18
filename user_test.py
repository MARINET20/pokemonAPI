import threading
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service

from main import run_flask_server


class SeleniumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flask_server_thread = threading.Thread(target=run_flask_server)
        cls.flask_server_thread.start()

    def setUp(self):
        self.driver = webdriver.Edge(service=Service('C:\\Temp\\msedgedriver.exe'))

    # вывод списка покемонов
    def test_page(self):
        self.driver.get('http://localhost:5000/')
        elements = self.driver.find_elements(By.CLASS_NAME, 'card-title')
        for element in elements:
            self.assertTrue(element.text)

    # поиск
    def test_search(self):
        self.driver.get('http://localhost:5000/')
        element = self.driver.find_element(By.ID, 'search')
        element.send_keys('pikachu')
        element.submit()

    # страница покемона
    def test_pokemon(self):
        self.driver.get('http://localhost:5000/pokemon/PIKACHU')
        element = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(element.text, 'pikachu')

    # ход игрока в бою
    def test_fight(self):
        self.driver.get('http://localhost:5000/fight/BULBASAUR')
        element = self.driver.find_element(By.ID, 'tentacles')
        element.send_keys('5')
        button = self.driver.find_element(By.XPATH, '//input[@type="submit"]')
        button.click()

    def tearDown(self):
        self.driver.close()

    @classmethod
    def tearDownClass(cls):
        cls.flask_server_thread.join()


if __name__ == '__main__':
    unittest.main()
