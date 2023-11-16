import pytest
import unittest
from main import app


class TestPokemonAPI(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        self.filters = {'type': 'fire'}

    def test_get_pokemon_list(self):
        response = self.app.get('/', query_string=self.filters)
        self.assertEqual(response.status_code, 200)

    def test_get_pokemon_by_name(self):
        pokemon_name = "pikachu"
        response = self.app.get(f'/pokemon/{pokemon_name}')
        self.assertEqual(response.status_code, 200)

    def test_get_fight_info(self):
        user_pokemon_name = "pikachu"
        response = self.app.get(f'/fight/{user_pokemon_name}')
        self.assertEqual(response.status_code, 200)

    def test_post_fight_info(self):
        user_pokemon_name = "pikachu"
        response = self.app.post(f'/fight/{user_pokemon_name}')
        self.assertEqual(response.status_code, 200)

    def test_get_quick_battle(self):
        name = "pikachu"
        response = self.app.get(f'/fight/fast/{name}')
        self.assertEqual(response.status_code, 200)

    def test_post_quick_battle(self):
        name = "pikachu"
        response = self.app.post(f'/fight/fast/{name}')
        self.assertEqual(response.status_code, 200)

    def test_get_pokemon_list_page(self):
        page_id = 2
        response = self.app.get(f'/?page={page_id}')
        self.assertEqual(response.status_code, 200)

    # def test_post_fight(self):
    #     user_input = 3
    #     response = self.app.post(f'/fight/{user_input}')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_get_fast_fight_result(self):
    #     response = self.app.get('/fight/fast')
    #     self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
