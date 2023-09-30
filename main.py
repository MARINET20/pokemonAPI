from flask import Flask, jsonify, render_template, request
import requests
import psycopg2

app = Flask(__name__)


def get_db_connection():
    pass


class Pokemon:
    def __init__(self, name, image):
        self.name = name
        self.image = image


@app.route('/', methods=['GET'])
def index():
    BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
    response = requests.get(BASE_URL)
    data = response.json()

    q = request.args.get('q', '')
    if q:
        pokemon_data = [(pokemon['name'], f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon['url'].split('/')[-2]}.png") for pokemon in data['results'] if q.lower() in pokemon['name'].lower()]
        search_query = q
    else:
        pokemon_data = [(pokemon['name'], f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon['url'].split('/')[-2]}.png") for pokemon in data['results']]

    pokemon_list = [Pokemon(name, image) for name, image in pokemon_data]

    return render_template('index.html', pokemon_list=pokemon_list, search_query=q)


if __name__ == '__main__':
    app.run(port=8000)
