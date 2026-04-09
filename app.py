from flask import Flask, render_template_string, request
import random

app = Flask(__name__)

html_code = """
<!DOCTYPE html>
<html>
<head>
<title>Quantum RL Robot Path Planning</title>
<style>
body { font-family: Arial; text-align:center; background:#FAFAFA; }
canvas { border:2px solid #333; margin-top:10px; }
input, button { margin:5px; padding:4px; }
</style>
</head>
<body>

<h2>Path Planning for Autonomous Robots Using Quantum RL</h2>

<form id="inputForm">
Grid Size: <input name="size" value="6" min="2"><br>
Start (row,col): <input name="start" value="0,0"><br>
Goal (row,col): <input name="goal" value="5,5"><br>

<button type="submit">Run Simulation</button>
<button type="button" id="resetBtn">Reset Obstacles</button>
</form>

<canvas id="gridCanvas"></canvas>

<script>
const canvas = document.getElementById("gridCanvas");
const ctx = canvas.getContext("2d");
const cellSize = 50;
let obstacles = [];

function drawGrid(gridSize, obstacles, start, goal, path, step){
    canvas.width = gridSize * cellSize;
    canvas.height = gridSize * cellSize;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for(let r = 0; r < gridSize; r++){
        for(let c = 0; c < gridSize; c++){
            ctx.strokeStyle = "#90A4AE";
            ctx.strokeRect(c * cellSize, r * cellSize, cellSize, cellSize);
        }
    }

    ctx.fillStyle = "#263238";
    obstacles.forEach(o => ctx.fillRect(o[1]*cellSize, o[0]*cellSize, cellSize, cellSize));

    ctx.fillStyle = "#2ECC71";
    ctx.fillRect(start[1]*cellSize, start[0]*cellSize, cellSize, cellSize);

    ctx.fillStyle = "#E74C3C";
    ctx.fillRect(goal[1]*cellSize, goal[0]*cellSize, cellSize, cellSize);

    if (path && step >= 0){
        ctx.strokeStyle = "#1E88E5";
        ctx.lineWidth = 3;
        ctx.beginPath();

        for (let i = 0; i <= step; i++){
            let r = path[i][0], c = path[i][1];
            let x = c*cellSize + cellSize/2;
            let y = r*cellSize + cellSize/2;
            i === 0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
        }
        ctx.stroke();

        let rr = path[step][0], cc = path[step][1];
        ctx.fillStyle = "#1565C0";
        ctx.beginPath();
        ctx.arc(cc*cellSize + cellSize/2, rr*cellSize + cellSize/2, cellSize/4, 0, Math.PI*2);
        ctx.fill();
    }
}

function animatePath(gridSize, obstacles, start, goal, path){
    let step = 0;
    drawGrid(gridSize, obstacles, start, goal, path, step);

    let timer = setInterval(() => {
        if (step < path.length - 1){
            step++;
            drawGrid(gridSize, obstacles, start, goal, path, step);
        } else {
            clearInterval(timer);
        }
    }, 400);
}

document.getElementById("inputForm").addEventListener("submit", function(e){
    e.preventDefault();

    const size = this.size.value;
    const start = this.start.value;
    const goal = this.goal.value;

    fetch(`/run?size=${size}&start=${start}&goal=${goal}&obs=${obstacles.map(o => o.join(",")).join(";")}`)
    .then(res => res.json())
    .then(data => {
        if (data.path.length <= 1){
            alert("No valid path found!");
        } else {
            animatePath(data.gridSize, data.obstacles, data.start, data.goal, data.path);
        }
    });
});

document.getElementById("resetBtn").addEventListener("click", function(){
    obstacles = [];
    drawGrid(6, [], [0,0], [5,5], [], -1);
});

canvas.addEventListener("click", function(event){
    const gridSize = Number(document.querySelector('input[name="size"]').value);

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const row = Math.floor(y / cellSize);
    const col = Math.floor(x / cellSize);

    const index = obstacles.findIndex(o => o[0] === row && o[1] === col);

    if (index === -1){
        obstacles.push([row, col]);
    } else {
        obstacles.splice(index, 1);
    }

    drawGrid(gridSize, obstacles, [0,0], [gridSize-1, gridSize-1], [], -1);
});
</script>

</body>
</html>"""
def quantum_inspired_rl(start, goal, obstacles, size):
    actions = [(-1,0),(0,1),(1,0),(0,-1)]

    def valid(pos):
        r,c = pos
        return 0 <= r < size and 0 <= c < size and pos not in obstacles

    from collections import deque
    queue = deque([start])
    parent = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break

        random.shuffle(actions)

        for a in actions:
            nxt = (current[0]+a[0], current[1]+a[1])
            if valid(nxt) and nxt not in parent:
                parent[nxt] = current
                queue.append(nxt)

    if goal not in parent:
        return [start]

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]

    return path[::-1]


@app.route("/")
def home():
    return render_template_string(html_code)


@app.route("/run")
def run():
    try:
        size = int(request.args.get("size"))
        start = tuple(map(int, request.args.get("start").split(",")))
        goal = tuple(map(int, request.args.get("goal").split(",")))

        obs_text = request.args.get("obs", "").strip()
        obstacles = set(tuple(map(int, o.split(","))) for o in obs_text.split(";") if o)

        path = quantum_inspired_rl(start, goal, obstacles, size)

        return {
            "gridSize": size,
            "start": start,
            "goal": goal,
            "obstacles": list(obstacles),
            "path": path
        }

    except Exception as e:
        return {
            "gridSize": 5,
            "start": (0, 0),
            "goal": (4, 4),
            "obstacles": [],
            "path": [(0, 0)]
        }


if __name__ == "__main__":
    app.run(debug=True)
