import math
import random
import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import json
import psycopg2
from flask_paginate import Pagination, get_page_args

app = Flask(__name__)

# Подключение к БД
conn = psycopg2.connect(
    host="localhost",
    database="Pokemons",
    user="postgres",
    password="0000"
)


def save_most_recent_pokemon(d):
    with open('pokemons.json', 'w') as f:
        json.dump(d, f)


def load_most_recent_pokemon():
    with open('pokemons.json', 'r') as f:
        return json.load(f)


def pokemon_json():
    with open('pokemons.json', 'r') as json_file:
        data_ = json.load(json_file)
        name = [pokemon['name'] for pokemon in data_]
    return name


global names
BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
response = requests.get(BASE_URL)
data = response.json()
results = data['results']
names = [pokemon['name'] for pokemon in data['results']]


@app.route('/', methods=['GET'])
def index():
    poke = []
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
    #     poke.append(d)

    page = request.args.get('page', type=int, default=1)
    per_page = 6
    offset = (page - 1) * per_page

    q = request.args.get('q', '')

    if q:
        pokemons = [pokemon for pokemon in load_most_recent_pokemon() if q.lower() in pokemon['name'].lower()]
    else:
        pokemons = load_most_recent_pokemon()

    total_pages = math.ceil(len(pokemons) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    pokemons = pokemons[start:end]

    return render_template('index.html', pokemons=pokemons, search_query=q, current_page=page, total_pages=total_pages,
                           poke=poke)


round_results = []
name = pokemon_json()
# opponent_pokemon = random.choice(name)


# img_opponent = pokemon_json(opponent_pokemon)
# print(img_opponent)


@app.route('/battle', methods=['GET', 'POST'])
def battle(opponent_pokemon=random.choice(name)):
    if request.method == 'GET':
        opponent_pokemon = random.choice(name)
    if request.method == 'POST':
        user_input = int(request.form['submit'])
        opponent_number = random.randint(1, 10)
        result_text = " Противник бьёт!"

        if user_input % 2 == opponent_number % 2:
            result_text = "Покемон пользователя наносит удар!"

        round_results.append({
            'user_input': user_input,  # вводимое число пользователя
            'opponent_number': opponent_number,  # рандомное число компьютера
            'result_text': result_text
        })
        # print(round_results)
        if len(round_results) == 3:
            # Выполнено три раунда, вычисляем итоговый результат
            user_wins = sum([1 for rnd in round_results if 'наносит удар' in rnd['result_text']])
            opponent_wins = 3 - user_wins
            game_score = str(user_wins) + ":" + str(opponent_wins)
            result_text = "Игра окончена!"
            if user_wins > opponent_wins:
                result = " Вы победили!"
                winner = "User"
            else:
                result = " Вы проиграли..."
                winner = "Opponent"

            # Insert the data into the database
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO results (winner, game_score, date) VALUES (%s, %s, %s)", (winner, game_score,
                                                                                       datetime.datetime.now()))
            conn.commit()

            return render_template('battle.html', round_results=round_results, user_wins=user_wins,
                                   opponent_wins=opponent_wins, opponent_pokemon=opponent_pokemon,
                                   result_text=result_text, opponent_number=opponent_number, result=result)

        elif len(round_results) == 1 or len(round_results) == 2:
            return render_template('battle.html', result_text=result_text, opponent_number=opponent_number, 
                                   opponent_pokemon=opponent_pokemon)
        else:
            opponent_pokemon = random.choice(name)
            return redirect(url_for('index',opponent_pokemon=opponent_pokemon))  # изменили на перенаправление на страницу index

    #opponent_pokemon = random.choice(name)
    round_results.clear()  # Очищаем результаты перед началом новой игры

    return render_template('battle.html', opponent_pokemon=opponent_pokemon)


@app.route('/read_json')
def read_json():
    with open('pokemons.json') as json_file:
        d = json.load(json_file)
    return d


if __name__ == '__main__':
    app.run(port=5000)
