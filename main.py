import ftplib
import math
import os
import random
import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
import json
import psycopg2
from flask_mail import Mail, Message
from ftplib import FTP
import markdown
import redis

app = Flask(__name__)

# Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Подключение к БД
conn = psycopg2.connect(
    host="localhost",
    database="Pokemons",
    user="postgres",
    password="0000"
)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8")


def send_email(email, result_battle):
    message = "Битва Покемонов"
    try:
        msg = Message(message, sender='noreply@demo.com',
                      recipients=[email])
        msg.body = result_battle
        mail.send(msg)
        return f"Результат отправлен на почту {email}"
    except Exception as e:
        return "Сообщение не отправилось..."


def save_most_recent_pokemon(pokemon):
    redis_client.set(pokemon['name'], json.dumps(pokemon))


# def save_most_recent_pokemon(d):
#     with open('pokemons.json', 'w') as f:
#         json.dump(d, f)


def load_most_recent_pokemon():
    with open('pokemons.json', 'r') as f:
        return json.load(f)


def load_most_recent_pokemon_redis(name):
    p_data = redis_client.get(name)
    if p_data:
        return json.loads(p_data)
    else:
        return None


def delete_pokemon_data(name):
    redis_client.delete(name)
    print(f"{name} успешно удален")


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
                img = pokemon['image_url']
    return attack, hp, img


global names
BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
response = requests.get(BASE_URL)
data = response.json()
results = data['results']
names = [pokemon['name'] for pokemon in data['results']]


@app.route('/', methods=['GET'])
def index():
    poke = []
    count = 1
    for name in names:
        pokemon = load_most_recent_pokemon_redis(name)
        #print(pokemon)
        if not pokemon:
            pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{name}'
            r = requests.get(pokemon_url).json()
            pokemon = {
                'id': r['id'],
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
            save_most_recent_pokemon(pokemon)
        poke.append(pokemon)
        count += 1
    # poke = []
    # count = 1
    # for name in names:
    #     pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{name}'
    #     r = requests.get(pokemon_url).json()
    #     d = {
    #         'id': r['id'],
    #         'name': r['name'],
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
    #     count += 1
    # save_most_recent_pokemon(poke)

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


@app.route('/fight/<name>', methods=['GET', 'POST'])
def fight(name):
    name = name.lower()
    global attack
    global hp
    global attack_pokemon
    global hp_pokemon
    global opponent_pokemon_name
    global user_pokemon
    global result
    global img
    global img_pokemon

    if request.method == 'GET':
        # opponent_pokemon = random.choice(names).upper()
        opponent_pokemon_name = random.choice(names)
        #attack, hp, img = pokemons_info_json(opponent_pokemon_name)
        opponent_pokemon_info = load_most_recent_pokemon_redis(opponent_pokemon_name)
        attack = opponent_pokemon_info['attack']
        hp = opponent_pokemon_info['hp']
        img = opponent_pokemon_info['image_url']
        #attack_pokemon, hp_pokemon, img_pokemon = pokemons_info_json(name)  # выбранный пользователем покемон
        user_pokemon_info = load_most_recent_pokemon_redis(name)
        attack_pokemon = user_pokemon_info['attack']
        hp_pokemon = user_pokemon_info['hp']
        img_pokemon = user_pokemon_info['image_url']
        user_pokemon = user_pokemon_info['name']
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

            return render_template('fight.html', result_text=result_text, opponent_pokemon_name=opponent_pokemon_name, name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result, img=img, img_pokemon=img_pokemon)
        else:
            user_input = int(request.form['submit'])
            opponent_number = random.randint(1, 10)

            print(hp, hp_pokemon)
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
                        (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now()))
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
                        (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now()))
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

            return render_template('fight.html', result_text=result_text, opponent_pokemon_name=opponent_pokemon_name, name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result, img=img, img_pokemon=img_pokemon)

    # return redirect(url_for('result.html'))

    # return redirect(url_for('index'))  # изменили на перенаправление на

    round_results.clear()  # Очищаем результаты перед началом новой игры
    return render_template('fight.html', opponent_pokemon_name=opponent_pokemon_name, name=name, hp=hp, hp_pokemon=hp_pokemon,
                           result=result, img=img, img_pokemon=img_pokemon)


# @app.route('/pokemon/<name>', methods=['GET'])
# def pokemon(name):
#     with open('pokemons.json') as json_file:
#         d = json.load(json_file)
#     # Нахождение покемона по имени в загруженных данных
#     pokemon = next((p for p in d if p['name'] == name), None)
#     return d


@app.route('/fight/fast/<name>', methods=['GET', 'POST'])
def quickBattle(name):
    name = name.lower()
    global attack
    global hp
    global attack_pokemon
    global hp_pokemon
    global opponent_pokemon_name
    global user_pokemon
    global result
    global img
    global img_pokemon
    # opponent_pokemon = random.choice(names).upper()
    #attack, hp, img = pokemons_info_json(opponent_pokemon)
    opponent_pokemon_info = load_most_recent_pokemon_redis(opponent_pokemon_name)
    attack = opponent_pokemon_info['attack']
    hp = opponent_pokemon_info['hp']
    img = opponent_pokemon_info['image_url']
    #attack_pokemon, hp_pokemon, img_pokemon = pokemons_info_json(name)  # выбранный пользователем покемон
    user_pokemon_info = load_most_recent_pokemon_redis(name)
    attack_pokemon = user_pokemon_info['attack']
    hp_pokemon = user_pokemon_info['hp']
    img_pokemon = user_pokemon_info['image_url']
    user_pokemon = user_pokemon_info['name']
    print(user_pokemon)
    result = ''
    while hp > 0 and hp_pokemon > 0:
        user_input = random.randint(1, 10)
        opponent_number = random.randint(1, 10)

        # print(user_input,opponent_number)
        if user_input % 2 == opponent_number % 2:
            hp = hp - attack_pokemon
            result_text = "Покемон пользователя наносит удар!"
            if hp <= 0:
                result = "Вы победили!"
                winner = "Пользователь"
                result_text = "Игра окончена!"

                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date) VALUES (%s, %s, %s, %s)",
                    (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now()))
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
                    (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now()))
                conn.commit()

        round_results.append({
            'user_input': user_input,
            'opponent_number': opponent_number,
            'hp': hp,
            'hp_pokemon': hp_pokemon,
            'attack': attack,
            'attack_pokemon': attack_pokemon,
            'result_text': result_text
        })

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

    if request.method == 'POST':
        if result != "":
            email = request.form.get('email')
            print(email)
            result_text_message = send_email(email, result)

        return render_template('fightFast.html', result_text=result_text, opponent_pokemon=opponent_pokemon_name,
                               name=name, hp=hp, hp_pokemon=hp_pokemon, result=result, round_results=round_results,
                               img=img, img_pokemon=img_pokemon, result_text_message=result_text_message)

    return render_template('fightFast.html', result_text=result_text, opponent_pokemon=opponent_pokemon_name,
                           name=name, hp=hp, hp_pokemon=hp_pokemon, result=result, round_results=round_results,
                           img=img, img_pokemon=img_pokemon)


@app.route('/pokemon/<name>', methods=['GET', 'POST'])
def pokemon(name):
    #print(name.lower())
    pokemon = load_most_recent_pokemon_redis(name.lower())
    #print(pokemon)
    if not pokemon:
        return None
    return render_template('pokemonInfo.html', pokemon=pokemon)


@app.route('/pokemon/save/<name>/<speed>/<hp>/<defense>/<attack>/<weight>', methods=['GET', 'POST'])
def save(name, speed, hp, defense, attack, weight):
    name = name.lower()
    USERNAME = ''
    PASSWORD = ''
    HOST = ''

    ftp = ftplib.FTP(HOST, USERNAME, PASSWORD)
    files = ftp.nlst()
    print(files)

    markdown_text = f"# {name}\n\nСкорость: {speed}\n\nЖизнь: {hp}\n\nЗащита: {defense}" \
                    f"\n\nАтака: {attack}\n\nВес: {weight}"

    file_name = f"{name}.md"
    current_date = datetime.datetime.now().strftime('%d.%m.%Y')

    if current_date in ftp.nlst():
        ftp.cwd(current_date)
    else:
        ftp.mkd(current_date)
        ftp.cwd(current_date)

    with open(current_date, 'wb') as f:
        f.write(markdown_text.encode())
    ftp.storbinary('STOR ' + file_name, open(current_date, 'rb'))

    ftp.quit()

    return render_template('savePokemon.html', name=name, speed=speed, hp=hp,
                           defense=defense, attack=attack, weight=weight)


if __name__ == '__main__':
    app.run(port=5000)
