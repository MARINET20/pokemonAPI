import datetime
import ftplib
import json
import math
import os
import random
from audioop import reverse
from urllib.parse import urlencode

import psycopg2
import redis
import requests
from flask import Flask, render_template, request, flash, redirect, url_for, g, session
from flask_mail import Mail, Message
import werkzeug
from prometheus_flask_exporter import PrometheusMetrics
from requests import post
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
import uuid

app = Flask(__name__)
login_manager = LoginManager(app)
metrics = PrometheusMetrics(app)

# config = configparser.ConfigParser()
# config.read('config.ini')
# print(config.read('config.ini'))
# print(config.get('Email', 'EMAIL_USERNAME'))

# Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = True
app.config['SECRET_KEY'] = ''
CLIENTID = ''
CLIENT_SECRET = ''
mail = Mail(app)


@login_manager.user_loader
def load_user(id):
    return UserLogin().fromDB(id)


# Подключение к БД
conn = psycopg2.connect(
    host="localhost",
    database='Pokemons',
    user='postgres',
    password='0000'
)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8")


def run_flask_server():
    app.run(port=5000)


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


def send_psw_to_email(email, random_psw):
    message = "Битва Покемонов"
    try:
        msg = Message(message, sender='pokemon@demo.com',
                      recipients=[email])
        msg.body = random_psw
        mail.send(msg)
        return "Введите пароль из сообщения"
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


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.search_form = None


@app.route('/', methods=['GET'])
def index():
    poke = []
    count = 1
    user = g.user
    for name in names:
        pokemon = load_most_recent_pokemon_redis(name)
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
                           user=user)


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
    opponent_pokemon_name = random.choice(names)
    opponent_pokemon_info = load_most_recent_pokemon_redis(opponent_pokemon_name)
    attack = opponent_pokemon_info['attack']
    hp = opponent_pokemon_info['hp']
    img = opponent_pokemon_info['image_url']
    user_pokemon_info = load_most_recent_pokemon_redis(name)
    attack_pokemon = user_pokemon_info['attack']
    hp_pokemon = user_pokemon_info['hp']
    img_pokemon = user_pokemon_info['image_url']
    user_pokemon = user_pokemon_info['name']
    result = ''
    rounds = 0
    if request.method == 'POST':
        if hp <= 0 or hp_pokemon <= 0:
            result_text = "Игра окончена!"
            if hp < hp_pokemon:
                result = "Вы победили!"
                winner = name
            elif hp > hp_pokemon:
                result = "Вы проиграли..."
                winner = opponent_pokemon_name
            else:
                result = "Ничья"
                winner = "Ничья"
            return render_template('fight.html', result_text=result_text, opponent_pokemon_name=opponent_pokemon_name,
                                   name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result, img=img, img_pokemon=img_pokemon)
        else:
            user_input = int(request.form['submit'])
            opponent_number = random.randint(1, 10)
            rounds += 1
            if user_input % 2 == opponent_number % 2:
                hp = hp - attack_pokemon
                result_text = "Покемон пользователя наносит удар!"
                if hp <= 0:
                    result = "Вы победили!"
                    winner = name
                    result_text = "Игра окончена!"

                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date, rounds) "
                        "VALUES (%s, %s, %s,%s, %s)",
                        (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now(), rounds))
                    conn.commit()
            else:
                hp_pokemon = hp_pokemon - attack
                result_text = " Противник бьёт!"
                if hp_pokemon <= 0:
                    result = "Вы проиграли..."
                    winner = opponent_pokemon_name
                    result_text = "Игра окончена!"

                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date, rounds) "
                        "VALUES (%s, %s, %s,%s, %s)",
                        (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now(), rounds))
                    conn.commit()
            # round_results.append({
            #     'user_input': user_input,  # вводимое число пользователя
            #     'opponent_number': opponent_number,  # рандомное число компьютера
            #     'hp': hp,
            #     'hp_pokemon': hp_pokemon,
            #     'attack': attack,
            #     'attack_pokemon': attack_pokemon,
            #     'result_text': result_text
            # })

            return render_template('fight.html', result_text=result_text, opponent_pokemon_name=opponent_pokemon_name,
                                   name=name,
                                   hp=hp, hp_pokemon=hp_pokemon, result=result, img=img, img_pokemon=img_pokemon)

    round_results.clear()  # Очищаем результаты перед началом новой игры
    return render_template('fight.html', opponent_pokemon_name=opponent_pokemon_name, name=name, hp=hp,
                           hp_pokemon=hp_pokemon,
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
    opponent_pokemon_info = load_most_recent_pokemon_redis(opponent_pokemon_name)
    attack = opponent_pokemon_info['attack']
    hp = opponent_pokemon_info['hp']
    img = opponent_pokemon_info['image_url']
    user_pokemon_info = load_most_recent_pokemon_redis(name)
    attack_pokemon = user_pokemon_info['attack']
    hp_pokemon = user_pokemon_info['hp']
    img_pokemon = user_pokemon_info['image_url']
    user_pokemon = user_pokemon_info['name']
    result = ''
    rounds = 0
    while hp > 0 and hp_pokemon > 0:
        user_input = random.randint(1, 10)
        opponent_number = random.randint(1, 10)
        rounds += 1
        if user_input % 2 == opponent_number % 2:
            hp = hp - attack_pokemon
            if hp <= 0:
                result = "Вы победили!"
                winner = name
                result_text = "Игра окончена!"

                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date, rounds) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now(), rounds))
                conn.commit()
        else:
            hp_pokemon = hp_pokemon - attack
            if hp_pokemon <= 0:
                result = "Вы проиграли..."
                winner = opponent_pokemon_name
                result_text = "Игра окончена!"

                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date, rounds) "
                    "VALUES (%s, %s, %s,%s, %s)",
                    (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now(), rounds))
                conn.commit()

    result_text = "Игра окончена!"
    if hp < hp_pokemon:
        result = "Вы победили!"
        winner = name
    elif hp > hp_pokemon:
        result = "Вы проиграли..."
        winner = opponent_pokemon_name
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
    name = name.lower()
    pokemon = load_most_recent_pokemon_redis(name)
    if not pokemon:
        return None
    return render_template('pokemonInfo.html', pokemon=pokemon)


@app.route('/pokemon/save/<name>/<speed>/<hp>/<defense>/<attack>/<weight>', methods=['GET', 'POST'])
def save(name, speed, hp, defense, attack, weight):
    name = name.lower()
    USERNAME = ''
    PASSWORD = ''
    HOST = 'localhost'

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    result_text_message = ''
    global random_number
    global user
    if request.method == 'POST':
        user = getUserByEmail(request.form['email'])
        password = getUserByPassword(request.form['email'])
        id = getUserById(request.form['email'])
        random_number = str(random.randint(10000, 99999))
        email = request.form.get('email')
        if user and check_password_hash(password, request.form['psw']):
            result_text_message = send_psw_to_email(email, random_number)
            return redirect(url_for('oauth'))

    return render_template('login.html')


@app.route('/oauth', methods=['GET', 'POST'])
def oauth():
    if request.method == 'POST':
        entered_psw = request.form.get('psw')
        if random_number == entered_psw:
            userlogin = UserLogin().create(user)
            rm = True
            login_user(userlogin, rm)
            return render_template('account.html')

    return render_template('oauth.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/account')
@login_required
def account():
    return render_template('account.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    global date
    global nameUser
    global emailUser
    global pswUser
    date = str(random.randint(10000, 99999))
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = addUser(request.form['email'])
            if res:
                email = request.form.get('email')
                result_text_message = send_psw_to_email(email, date)
                nameUser = request.form['name']
                emailUser = email
                pswUser = hash
                return redirect(url_for('callback'))

            else:
                count = 1
                message_text = "Пользователь с такой почтой уже существует!"
                render_template('registration.html', message_text=message_text, title='Registration')
        else:
            message_text = "Неверное заполнение поля"
            render_template('registration.html', message_text=message_text, title='Registration')

    return render_template('registration.html', title='Registration')


@app.route('/callback', methods=['GET', 'POST'])
def callback():
    if request.method == 'POST':
        entered_psw = request.form.get('psw')
        if date == entered_psw:
            addUserDB(nameUser, emailUser, pswUser)
            return redirect(url_for('login'))

    return render_template('callback.html', title='Registration')


@app.route('/recover/password', methods=['GET', 'POST'])
def forgotPassword():
    global password
    global hash
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        getPassword = getUserByEmail(email)[2]
        if getPassword == request.form['email'] \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            random_psw = str(random.randint(10000, 99999))
            rndText = send_psw_to_email(email, random_psw)
            redirect(url_for('sendPassword'))
    return render_template('password/forgotPassword.html', title='Восстановление пароля')


@app.route('/recover/password/input', methods=['GET', 'POST'])
def sendPassword():
    return render_template('password/forgotPassword.html', title='Восстановление пароля')


@app.route('/YandexID')
def YandexID():
    if request.args.get('code', False):
        data_ = {
            'grant_type': 'authorization_code',
            'code': request.args.get('code'),
            'client_id': CLIENTID,
            'client_secret': CLIENT_SECRET
        }
        data_ = urlencode(data_)
        oauthjson = post('https://oauth.yandex.ru/' + "token", data_).json()
        userinfo = requests.get('https://login.yandex.ru/info',
                                headers={'Authorization': 'OAuth' + oauthjson['access_token']}).json()
        addUserDB(None, userinfo["default_email"], None)
        username = getUserByEmail(userinfo["default_email"])
        print(username)
        login_user(UserLogin().create(username), True)

        return redirect(url_for('index'))

    return redirect('https://oauth.yandex.ru/' + "authorize?response_type=code&client_id={}".format(CLIENTID))


# token = y0_AgAEA7qkZDnpAArr3AAAAADzfR787NjxVoYlTtmomwdea3sGtz34S5Q

def addUserDB(name, email, hashed_psw):
    user_id = str(uuid.uuid4())
    try:
        cur = conn.cursor()
        timestamp = datetime.datetime.now()
        cur.execute("INSERT INTO users VALUES(%s,%s, %s, %s,%s)", (user_id, name, email, hashed_psw, timestamp))
        conn.commit()
    except psycopg2.Error as e:
        print("Error adding user to the database " + str(e))
        return False
    return True


def addUser(email):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) as count FROM users WHERE email LIKE '{email}'")
        res = cur.fetchone()
        if res[0] > 0:
            print("A user with this email already exists")
            return False
    except psycopg2.Error as e:
        print("Error adding user to the database " + str(e))
        return False
    return True


def getUser(id):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE id LIKE '{id}'")
        res = cur.fetchone()
        if not res:
            return None
        return res
    except psycopg2.Error as e:
        print("Ошибка получения данных из БД " + str(e))
        return None


def getUserByEmail(email):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE email LIKE '{email}'")
        res = cur.fetchone()
        if not res:
            return False
        return res
    except psycopg2.Error as e:
        print("Ошибка получения данных из БД " + str(e))
    return False


def getUserByPassword(email):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT psw FROM users WHERE email LIKE '{email}'")
        res = cur.fetchone()
        if not res:
            return False
        return res[0]
    except psycopg2.Error as e:
        print("Ошибка получения данных из БД " + str(e))
    return False


def getUserById(email):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT id FROM users WHERE email LIKE '{email}'")
        res = cur.fetchone()
        if not res:
            return False
        return res[0]
    except psycopg2.Error as e:
        print("Ошибка получения данных из БД " + str(e))
    return False


class UserLogin:
    def fromDB(self, id):
        self.__user = getUser(id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user[0])


if __name__ == '__main__':
    app.run(port=5000)
