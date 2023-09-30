import requests

BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
response = requests.get(f"{BASE_URL}")
data = response.json()
names = [pokemon['name'] for pokemon in data['results']]
urls = [pokemon['url'] for pokemon in data['results']]
print(data)

pokeImages = []
for pokemon in data['results']:
    pokeID = pokemon['url'].split('/')[-2]
    pokeImage = f"<img src='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokeID}.png'>"
    pokeImages.append(pokeImage)

#print(pokeImages)