from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)


@app.route('/')
def index():
    BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
    response = requests.get(f"{BASE_URL}")
    data = response.json()
    names = [pokemon['name'] for pokemon in data['results']]
    return render_template('index.html', names=names)
# def get_pokemon_names():
#     BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
#     response = requests.get(f"{BASE_URL}")
#     data = response.json()
#     names = [pokemon['name'] for pokemon in data['results']]
#     return jsonify(names)


if __name__ == '__main__':
    app.run(port=8000)
