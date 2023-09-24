from flask import Flask, jsonify
import requests

app = Flask(__name__)


@app.route('/')
def get_pokemon_names():
    BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
    response = requests.get(f"{BASE_URL}")
    data = response.json()
    names = [pokemon['name'] for pokemon in data['results']]
    return jsonify(names)


@app.route('/about')
def about():
    return 'Здесь будет информация об авторе сайта.'


if __name__ == '__main__':
    app.run(port=8000)
