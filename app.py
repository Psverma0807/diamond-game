from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, emit
import random
import string
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
games = {}

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Game:
    def __init__(self):
        self.players = {}
        self.inputs = {}
        self.round = 1
        self.king = None

    def add_player(self, name):
        if len(self.players) < 5:
            self.players[name] = 0

    def start(self):
        self.king = random.choice(list(self.players.keys()))

    def calculate(self):
        avg = sum(self.inputs.values()) / len(self.inputs)
        closest = min(self.inputs, key=lambda x: abs(self.inputs[x] - avg))

        for p in self.players:
            if p == closest:
                self.players[p] += 1
            else:
                self.players[p] -= 1

        return avg, closest


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/game')
def game():
    return render_template('game.html')


@socketio.on('create_game')
def create_game():
    key = generate_key()
    games[key] = Game()
    emit('game_created', key)


@socketio.on('join_game')
def join_game(data):
    print("JOIN EVENT:", data)  

    key = data['key']
    name = data['name']

    if key in games:
        game = games[key]
        game.add_player(name)
        join_room(key)

        emit('update_players', list(game.players.keys()), room=key)

        if len(game.players) == 5:
            game.start()
            emit('game_start', room=key)


@socketio.on('submit_number')
def submit_number(data):
    key = data['key']
    name = data['name']
    num = int(data['number'])

    game = games[key]
    game.inputs[name] = num

    if len(game.inputs) == len(game.players):
        avg, closest = game.calculate()
        game.inputs = {}

        emit('round_result', {
            'avg': round(avg, 2),
            'closest': closest,
            'scores': game.players
        }, room=key)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
