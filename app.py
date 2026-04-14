import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"

socketio = SocketIO(app, cors_allowed_origins="*")

# ---------------- GAME STATE ----------------
rooms = {}

def generate_room():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_diamonds():
    return [
        {"id": i, "x": random.randint(50, 500), "y": random.randint(50, 400)}
        for i in range(10)
    ]

# ---------------- JOIN GAME ----------------
@socketio.on("join_game")
def join_game(data):
    room = data.get("room")

    if not room:
        room = generate_room()

    join_room(room)

    if room not in rooms:
        rooms[room] = {
            "players": {},
            "diamonds": create_diamonds()
        }

    rooms[room]["players"][request.sid] = {"score": 0}

    emit("room_joined", {
        "room": room,
        "diamonds": rooms[room]["diamonds"],
        "players": rooms[room]["players"]
    }, room=room)

# ---------------- COLLECT DIAMOND ----------------
@socketio.on("collect_diamond")
def collect_diamond(data):
    room = data["room"]
    diamond_id = data["diamond_id"]
    sid = request.sid

    if room not in rooms:
        return

    # remove diamond
    rooms[room]["diamonds"] = [
        d for d in rooms[room]["diamonds"] if d["id"] != diamond_id
    ]

    # update score
    if sid in rooms[room]["players"]:
        rooms[room]["players"][sid]["score"] += 1

    emit("game_update", {
        "diamonds": rooms[room]["diamonds"],
        "players": rooms[room]["players"]
    }, room=room)

# ---------------- DISCONNECT ----------------
@socketio.on("disconnect")
def disconnect():
    for room in list(rooms.keys()):
        if request.sid in rooms[room]["players"]:
            del rooms[room]["players"][request.sid]

            emit("game_update", {
                "diamonds": rooms[room]["diamonds"],
                "players": rooms[room]["players"]
            }, room=room)

            break

# ---------------- ROUTE ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)