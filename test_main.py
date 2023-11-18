import unittest
import json
import requests

from main import app
import unittest
from selenium import webdriver
from main import run_flask_server
import threading
import time
from selenium.webdriver.chrome.service import Service


class TestPokemonAPI(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.filters = {'type': 'fire'}

    def test_get_pokemon_list(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get_pokemon_by_name(self):
        pokemon_name = "pikachu"
        attack = 55
        hp = 35
        response = self.app.get(f'/pokemon/{pokemon_name}')
        self.assertEqual(response.status_code, 200)
        pokemon = response.data.decode('utf-8')
        self.assertIn(f'<h1 class="text-center">{pokemon_name}</h1>', pokemon)
        self.assertIn(f'<h5 class="card-text">Атака: {attack}</h5>', pokemon)
        self.assertIn(f'<h5 class="card-text">Жизнь: {hp}</h5>', pokemon)

    def test_fight(self):
        user_pokemon_name = 'charizard'
        opponent_pokemon_info = {
            "name": "bulbasaur",
            "attack": 65,
            "hp": 60,
        }

        response = self.app.post(f'/fight/{user_pokemon_name}', data={'submit': 2,
                                                                      'opponent_pokemon_name': 'bulbasaur',
                                                                      'attack': 65,
                                                                      'hp': 60})
        self.assertEqual(response.status_code, 200)
        #print(response.data)

    def test_quick_fight(self):
        name = "pikachu"
        response = self.app.post(f'/fight/fast/{name}', data={
                                                              'opponent_pokemon_name': 'bulbasaur',
                                                              'attack': 65,
                                                              'hp': 60})

    def test_pokemon_list_page(self):
        pokemon_name = "METAPOD"
        speed = 30
        defense = 55
        page_id = 2
        response = self.app.get(f'/?page={page_id}')
        self.assertEqual(response.status_code, 200)
        pokemon = response.data.decode('utf-8')
        self.assertIn(f'<h4 class="card-title" id="name" data-bs-toggle="modal" data-bs-target="#exampleModal">{pokemon_name}</h4>', pokemon)
        # self.assertIn(f'<h5 class="card-text" id="speed"> Скорость: {speed}</h5>', pokemon)
        # self.assertIn(f'<h5 class="card-text" id="defense"> Защита: {defense}</h5>', pokemon)

    def test_save_pokemon(self):
        response = app.test_client().post('/pokemon/save/bulbasaur/45/60/50/65/10',
                                          data={'server': 'localhost', 'login': 'user', 'password': '12345678'})
        self.assertEqual(response.status_code, 200)

    def test_result(self):
        response = self.app.post('/fight/fast/bulbasaur',
                                 data={'send_type': 'db', 'event': 'test event saved!'})
        self.assertEqual(response.status_code, 200)
        response = self.app.post('/fight/fast/bulbasaur',
                                 data={'send_type': 'mail', 'event': 'test event saved!',
                                       'email': 'lisachekanova@gmail.com'})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
