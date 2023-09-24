import requests

BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
response = requests.get(f"{BASE_URL}")
data = response.json()
names = [pokemon['name'] for pokemon in data['results']]
urls = [pokemon['url'] for pokemon in data['results']]
print(urls)