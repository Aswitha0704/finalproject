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
</html>
