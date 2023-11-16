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

    # def test_get_pokemon_by_id(self):
    #     pokemon_id = 1
    #     response = self.app.get(f'/pokemon/{pokemon_id}')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_get_random_pokemon(self):
    #     response = self.app.get('/pokemon/random')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_get_fight_info(self):
    #     user_pokemon_id = 1
    #     opponent_pokemon_id = 2
    #     response = self.app.get(f'/fight?user_pokemon={user_pokemon_id}&opponent_pokemon={opponent_pokemon_id}')
    #     self.assertEqual(response.status_code, 200)
    #
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
