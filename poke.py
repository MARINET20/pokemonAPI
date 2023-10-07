from random import randint
from typing import List
import concurrent.futures
import requests, json, random
import asyncio
import aiohttp


def save_most_recent_pokemon(d):
    with open('pokemons.json', 'w') as f:
        json.dump(d, f)


def load_most_recent_pokemon():
    with open('pokemons.json', 'r') as f:
        return json.load(f)


def pokemon_json(pokemon):
    # with open('pokemons.json', 'r') as json_file:
    #     data_ = json.load(json_file)
    # for entry in data_:
    #     if entry['name'] == pokemon:
    #         return entry['image_url']
    pass


if __name__ == '__main__':
    BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
    response = requests.get(BASE_URL)
    data = response.json()
    results = data['results']
    names = [pokemon['name'] for pokemon in data['results']]

    name = [pokemon['name'] for pokemon in data['results']]
    opponent_pokemon = random.choice(names)
    print(opponent_pokemon)
    # img_opponent = pokemon_json(opponent_pokemon)
    print(pokemon_json(opponent_pokemon))
    # pokemons = []
    #
    # BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
    # response = requests.get(BASE_URL)
    # data = response.json()
    # results = data['results']
    # names = [pokemon['name'] for pokemon in data['results']]
    #
    # urls = [f"https://pokeapi.co/api/v2/pokemon/{name}" for name in names]
    # for name in names:
    #     pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{name}'
    #     r = requests.get(pokemon_url).json()
    #     d = {
    #         'name': r['name'].upper(),
    #         'speed': r['stats'][-1]['base_stat'],
    #         'defense': r['stats'][2]['base_stat'],
    #         'special_defense': r['stats'][4]['base_stat'],
    #         'attack': r['stats'][1]['base_stat'],
    #         'special_attack': r['stats'][3]['base_stat'],
    #         'hp': r['stats'][0]['base_stat'],
    #         'weight': r['weight'],
    #         'image_url': r['sprites']['other']['dream_world']['front_default']
    #     }
    #     pokemons.append(d)
    # recent_pokemon_data = save_most_recent_pokemon(pokemons)

# pokemons = []
# for result in results:
#     pokemon_url = f'https://pokeapi.co/api/v2/pokemon/1'
#     r = requests.get(baseapi).json()
#     d = {
#         'number': number,
#         'name': r['name'].upper(),
#         'speed': r['stats'][-1]['base_stat'],
#         'defense': r['stats'][2]['base_stat'],
#         'special_defense': r['stats'][4]['base_stat'],
#         'attack': r['stats'][1]['base_stat'],
#         'special_attack': r['stats'][3]['base_stat'],
#         'hp': r['stats'][0]['base_stat'],
#         'weight': r['weight'],
#         'image_url': r['sprites']['other']['dream_world']['front_default']
#     }
#     pokemons.append(d)
# recent_pokemon_data = load_most_recent_pokemon()

# BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
# response = requests.get(f"{BASE_URL}")
# data = response.json()
#
# names = [pokemon['name'] for pokemon in data['results']]
# urls = [pokemon['url'] for pokemon in data['results']]
#
#
# # def get_base_experience(data_):
# #     names_ = [pokemon['name'] for pokemon in data_['results']]
# #     urls_ = [f"https://pokeapi.co/api/v2/pokemon/{name}" for name in names_]
# #     for url in urls_:
# #         base_experience = requests.get(url).json()["base_experience"]
# #     return base_experience
#
# print(requests.get("https://pokeapi.co/api/v2/pokemon/1").json()["base_experience"])
# pokeInfo = [f"https://pokeapi.co/api/v2/pokemon/{name}" for name in names]
# base_experience = []
#
#
# def get_base_experience(info):
#     response = requests.get(info).json()["base_experience"]
#     return response
#
#
# with concurrent.futures.ThreadPoolExecutor() as executor:
#     results = executor.map(get_base_experience, pokeInfo)
#     print(results)
#     base_experience = list(results)
#
# print(base_experience)


# pokeInfo = [f"https://pokeapi.co/api/v2/pokemon/{name}" for name in names]
# base_experience = [requests.get(pokeInfo).json()["base_experience"]]
# print(base_experience)

# URL = f"https://pokeapi.co/api/v2/pokemon/1"
# UA = {"User-Agent": "TestScript; my@email.com; python3.9; requests"}
# r = requests.get(url=URL, headers=UA).json()
# abilities = [r["name"]]
# [abilities.append(ability["ability"]["name"]) for ability in r["abilities"]]
# base_experience = [ability["base_experience"] for ability in r["abilities"]]
# print(base_experience)


# for pokemon in data['results']:
#     pokeID = pokemon['url'].split('/')[-2]
#     URL = f"https://pokeapi.co/api/v2/pokemon/{pokeID}"
#     UA = {"User-Agent": "TestScript; my@email.com; python3.9; requests"}
#     r = requests.get(url=URL, headers=UA).json()
#     print(r)
#     abilities = [r["name"]]
#     [abilities.append(ability["ability"]["name"]) for ability in r["abilities"]]

# for pokemon in data['results']:
#     #print(pokemon)
#     pokeID = pokemon['url'].split('/')[-2]
#     print(pokeID)
#     pokeInfo = f"https://pokeapi.co/api/v2/item/{pokeID}"
#     #print(pokeInfo)
#     response = requests.get(pokeInfo)
#     data = response.json()
#     print(data)

# pokeInfo = f"https://pokeapi.co/api/v2/item/{names}"
# response = requests.get(pokeInfo)
# data = response.json()
# print(data)
# abilities = []
# for url in urls:
#     response = requests.get(url)
#     pokemon_data = response.json()
#     abilities.append(pokemon_data['abilities'])
# print(abilities)

# abilities = []
# pokeInfo = []
# for pokemon in data['results']:
#     pokeID = pokemon['url'].split('/')[-2]
#     pokeInfo = f"https://pokeapi.co/api/v2/item/{pokeID}"
#     response = requests.get(pokeInfo)
#     data = response.json()
#     print(data)
# 'https://pokeapi.co/api/v2/type/{id or name}/'
# print(data)
#
# pokeImages = []
# for pokemon in data['results']:
#     pokeID = pokemon['url'].split('/')[-2]
#     pokeImage = f"<img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokeID}.png'>"
#     pokeImages.append(pokeImage)

# print(pokeImages)

# pokemons_ability = []
# for i in urls:
#     pokemon = requests.get(f'{i}').json()
#     ability_n = len(pokemon['abilities'])
#     ability = [pokemon['abilities'][j]['ability']['name'] for j in range(ability_n)]
#     #print(ability)
#     pokemons_ability.append(ability)

# print(pokemons_ability)
# pokeInfo = []
# for pokemon in data['results']:
#     pokeID = pokemon['url'].split('/')[-2]
#     pokeInfo = f"<src='https://pokeapi.co/api/v2/ability/{pokeID}'>"
#     pokeInfo.append(str(pokeInfo))
# pokeInfo = []
# for pokemon in data['results']:
#     pokeID = pokemon['url'].split('/')[-2]
#     pokeInfo = f"<src='https://pokeapi.co/api/v2/ability/{pokeID}'>"
#     print(pokeInfo)


# старая версия проги
# pokemons = []
#
# BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
# response = requests.get(BASE_URL)
# data = response.json()
#
# names = [pokemon['name'] for pokemon in data['results']]
# q = request.args.get('q', '')
# if q:
#     pokemon_data = [(pokemon['name'],
#                      f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon['url'].split('/')[-2]}.png")
#                     for pokemon in data['results'] if q.lower() in pokemon['name'].lower()]
#     search_query = q
# else:
#     pokemon_data = [(pokemon['name'],
#                      f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon['url'].split('/')[-2]}.png")
#                     for pokemon in data['results']]
#
# pokemon_list = [Pokemon(name, image) for name, image in pokemon_data]
#
# return render_template('index.html', pokemon_list=pokemon_list, search_query=q)
# pokemon_list = ['Pikachu', 'Charmander', 'Squirtle', 'Bulbasaur']
# pokemon = random.choice(pokemon_list)
# rounds = 3
# user_score = 0
# enemy_score = 0
# for i in range(rounds):
#     user_choice = random.randint(1, 10)
#     enemy_choice = random.randint(1, 10)
#     if user_choice % 2 == enemy_choice % 2:
#         user_score += 1
#     else:
#         enemy_score += 1
#     if user_score > enemy_score:
#         result = 'Победа!'
#     elif user_score < enemy_score:
#         result = 'Проигрыш...'
#     else:
#         result = 'Ничья'
#
# print(result)
