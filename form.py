import psycopg2
import random
import datetime
import requests



BASE_URL = 'https://pokeapi.co/api/v2/pokemon?limit=151'
response = requests.get(BASE_URL)
data = response.json()
results = data['results']
names = [pokemon['name'] for pokemon in data['results']]


# Создайте цикл для вставки рандомных данных
for _ in range(30):  # Здесь 10 - количество раз, которое нужно выполнить вставку
    user_pokemon = random.choice(names)
    opponent_pokemon_name = random.choice(names)
    winner = random.choice([user_pokemon, opponent_pokemon_name])
    rounds = random.randint(1,3)

    # Замените параметры подключения к вашей базе данных
    conn = psycopg2.connect(
        host="localhost",
        database='Pokemons',
        user='postgres',
        password='0000'
    )

    # Затем выполните вставку данных с использованием случайных значений
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO results (user_pokemon, opponent_pokemon, winner, date, rounds) "
        "VALUES (%s, %s, %s,%s, %s)",
        (user_pokemon, opponent_pokemon_name, winner, datetime.datetime.now() - datetime.timedelta(days=2), rounds))

    conn.commit()

# Не забудьте закрыть соединение с базой данных
conn.close()