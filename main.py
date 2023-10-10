import math
import os
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


def is_json_empty():
    file_size = os.path.getsize('pokemons.json')
    if file_size == 0:
        return True
    with open('pokemons.json', 'r') as f:
        d = json.load(f)
        if not d:
            return True
    return False


def pokemons_info_json(name):
    with open('pokemons.json', 'r') as json_file:
        data_ = json.load(json_file)
        for pokemon in data_:
            if pokemon['name'] == name:
                attack = pokemon['attack']
                hp = pokemon['hp']
    return attack, hp


global names
BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
response = requests.get(BASE_URL)
data = response.json()
results = data['results']
names = [pokemon['name'] for pokemon in data['results']]


@app.route('/', methods=['GET'])
def index():
    if is_json_empty == True:
        poke = []
        for name in names:
            pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{name}'
            r = requests.get(pokemon_url).json()
            d = {
                'name': r['name'],
                'speed': r['stats'][-1]['base_stat'],
                'defense': r['stats'][2]['base_stat'],
                'special_defense': r['stats'][4]['base_stat'],
                'attack': r['stats'][1]['base_stat'],
                'special_attack': r['stats'][3]['base_stat'],
                'hp': r['stats'][0]['base_stat'],
                'weight': r['weight'],
                'image_url': r['sprites']['other']['dream_world']['front_default']
            }
            poke.append(d)
        save_most_recent_pokemon(poke)

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

    return render_template('index.html', pokemons=pokemons, search_query=q, current_page=page, total_pages=total_pages)


round_results = []


@app.route('/battle/<name>', methods=['GET', 'POST'])
def battle(name):
    global attack
    global hp
    global attack_pokemon
    global hp_pokemon
    global opponent_pokemon
    global user_pokemon
    global result

    if request.method == 'GET':
        opponent_pokemon = random.choice(names)
        attack, hp = pokemons_info_json(opponent_pokemon)
        attack_pokemon, hp_pokemon = pokemons_info_json(name)  # выбранный пользователем покемон
        user_pokemon = name
        result = ''
    if request.method == 'POST':
        if hp <= 0 or hp_pokemon <= 0:
            print(hp, hp_pokemon, " sorry")
            # вычисляем итоговый результат
            result_text = "Игра окончена!"
            if hp < hp_pokemon:
                result = "Вы победили!"
                winner = "Пользователь"
            elif hp > hp_pokemon:
                result = "Вы проиграли..."
                winner = "Враг"
            else:
                result = "Ничья"
                winner = "Ничья"

            return render_template('battle.html', result_text=result_text, opponent_pokemon=opponent_pokemon, name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result)
        else:
            user_input = int(request.form['submit'])
            opponent_number = random.randint(1, 10)

            print(hp,hp_pokemon)
            if user_input % 2 == opponent_number % 2:
                # отнимаем от жизни оппонента кол-во атак пользовательского покемона
                hp = hp - attack_pokemon
                result_text = "Покемон пользователя наносит удар!"
                if hp <= 0:
                    result = "Вы победили!"
                    winner = "Пользователь"
                    result_text = "Игра окончена!"

                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date) VALUES (%s, %s, %s,%s)",
                        (user_pokemon, opponent_pokemon, winner, datetime.datetime.now()))
                    conn.commit()
            else:
                hp_pokemon = hp_pokemon - attack
                result_text = " Противник бьёт!"
                if hp_pokemon <= 0:
                    result = "Вы проиграли..."
                    winner = "Враг"
                    result_text = "Игра окончена!"

                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date) VALUES (%s, %s, %s,%s)",
                        (user_pokemon, opponent_pokemon, winner, datetime.datetime.now()))
                    conn.commit()
            print(hp, hp_pokemon)
            round_results.append({
                'user_input': user_input,  # вводимое число пользователя
                'opponent_number': opponent_number,  # рандомное число компьютера
                'hp': hp,
                'hp_pokemon': hp_pokemon,
                'attack': attack,
                'attack_pokemon': attack_pokemon,
                'result_text': result_text
            })

            return render_template('battle.html', result_text=result_text, opponent_pokemon=opponent_pokemon, name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result)

    # return redirect(url_for('result.html'))

    # return redirect(url_for('index'))  # изменили на перенаправление на

    round_results.clear()  # Очищаем результаты перед началом новой игры
    return render_template('battle.html', opponent_pokemon=opponent_pokemon, name=name, hp=hp, hp_pokemon=hp_pokemon,
                           result=result)


@app.route('/read_json')
def read_json():
    with open('pokemons.json') as json_file:
        d = json.load(json_file)
    return d


if __name__ == '__main__':
    app.run(port=5000)
