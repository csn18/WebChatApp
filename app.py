import datetime
import time
from functools import wraps
from os import environ as env

import jwt
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'myConfig'
socketio = SocketIO(app)


def db_connect():
    retry_count = int(env.get('DB_RETRY_COUNT', 5))
    for i in range(retry_count):
        try:
            return mysql.connector.connect(
                host=env.get('DB_HOST', '127.0.0.1'),
                user=env.get('DB_USER', 'root'),
                passwd=env.get('DB_PASSWORD', '4252'),
                database=env.get('DB_NAME', 'chat')
            )
        except mysql.connector.errors.InterfaceError:
            time.sleep(5)
    raise mysql.connector.errors.InterfaceError(msg='Database start timeout exceeded')


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    data = query_fetchone(f'SELECT * FROM user WHERE username ="{username}" and password="{password}"')

    if data:
        token = query_fetchall(f'SELECT token FROM user WHERE username="{username}"')[0]

        response = redirect(url_for('chat'))
        response.set_cookie('token', token)
        response.set_cookie('username', username)
        return response

    else:
        if request.form['username'] and request.form['password']:
            session['logged_in'] = True
            token = jwt.encode({
                'user': request.form['username'],
                'exp': datetime.datetime.max
            },
                app.config['SECRET_KEY']).decode('utf-8')

            insert_db('INSERT INTO user (username, password, token) VALUE (%s,%s,%s)', (username, password, token))

            response = redirect(url_for('chat'))
            response.set_cookie('token', token)
            response.set_cookie('username', username)
            return response


def check_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return '<h1>Токен отсутствует</h1>'
        try:
            jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return '<h1>Неверный токен</h1>'
        return func(*args, **kwargs)

    return wrapped


@app.route('/chat')
@check_token
def chat():
    token = request.cookies.get('token')

    username = query_fetchall(f'SELECT username FROM user WHERE token="{token}"')[0]

    history = query_fetchall('SELECT * FROM history')

    return render_template('chat.html',
                           username=username,
                           history=history,
                           )


@socketio.on('send_message')
def handle_send_message_event(data):
    insert_db('INSERT INTO history (username, message, time) VALUE (%s,%s,%s)',
              (data['username'], data['message'], data['time']))

    socketio.emit('receive_message', data)


clients_online = {}


@socketio.on('user_connect')
def user_connect(data):
    username = data['username']
    clients_online[request.sid] = username

    all_users = list(set(clients_online.values()))

    socketio.emit('users', all_users)


@socketio.on('disconnect')
def disconnect():
    del clients_online[request.sid]

    all_users = list(set(clients_online.values()))
    socketio.emit('users', all_users)


def query_fetchall(query):
    cursor = mydb.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    result = [i[0] if len(i) == 1 else i for i in result]
    return result


def query_fetchone(query):
    print(mydb)
    cursor = mydb.cursor(buffered=True)
    cursor.execute(query)
    result = cursor.fetchone()
    return result


def insert_db(insert, value):
    cursor = mydb.cursor()
    cursor.execute(insert, value)
    mydb.commit()


if __name__ == '__main__':
    mydb = db_connect()
    socketio.run(app,
                 debug=env.get('DEBUG', True),
                 host=env.get('SERVER_HOST', '0.0.0.0'),
                 port=env.get('SERVER_PORT', '5000')
                 )
