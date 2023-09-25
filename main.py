from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
    response = requests.get(BASE_URL)
    data = response.json()

    q = request.args.get('q', '')
    if q:
        names = [pokemon['name'] for pokemon in data['results'] if q.lower() in pokemon['name'].lower()]
        search_query = q
    else:
        names = [pokemon['name'] for pokemon in data['results']]

    return render_template('index.html', names=names, search_query=q)


if __name__ == '__main__':
    app.run(port=8000)
