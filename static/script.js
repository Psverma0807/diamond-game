
const socket = io();

let room = null;

// ---------------- JOIN GAME ----------------
socket.emit("join_game", { room: null });

socket.on("room_joined", (data) => {
    room = data.room;
    renderDiamonds(data.diamonds);
    updateScores(data.players);
});

// ---------------- UPDATE GAME ----------------
socket.on("game_update", (data) => {
    renderDiamonds(data.diamonds);
    updateScores(data.players);
});

// ---------------- COLLECT ----------------
function collectDiamond(id) {
    socket.emit("collect_diamond", {
        room: room,
        diamond_id: id
    });
}

// ---------------- RENDER DIAMONDS ----------------
function renderDiamonds(diamonds) {
    const game = document.getElementById("game");
    game.innerHTML = "";

    diamonds.forEach(d => {
        const div = document.createElement("div");
        div.className = "diamond";
        div.style.left = d.x + "px";
        div.style.top = d.y + "px";

        div.onclick = () => collectDiamond(d.id);

        game.appendChild(div);
    });
}

// ---------------- SCOREBOARD ----------------
function updateScores(players) {
    const board = document.getElementById("scoreboard");
    board.innerHTML = "<h3>Scores</h3>";

    Object.values(players).forEach(p => {
        const pTag = document.createElement("div");
        pTag.innerText = "Score: " + p.score;
        board.appendChild(pTag);
    });
}