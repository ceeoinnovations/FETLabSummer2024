function initializePopup() {
    const popup = document.getElementById("popup");
    const yesButton = document.getElementById("yesButton");
    const noButton = document.getElementById("noButton");

    window.showPopup = function() {
        popup.classList.remove("fade-out");
        popup.classList.add("fade-in");
        popup.style.display = "block";
    }

    function hidePopup(val) {
        if (val === 1) {
            console.log("Simulation started");
            runAISimulation();
        } else {
            console.log("Simulation ended");
            window.gameStarted = true;
        }
        popup.classList.remove("fade-in");
        popup.classList.add("fade-out");
    }

    yesButton.addEventListener("click", function() { hidePopup(1); });
    noButton.addEventListener("click", function() { hidePopup(0); });

    popup.addEventListener("transitionend", function() {
        console.log('fading popup');
        if (popup.classList.contains("fade-out")) {
            popup.style.display = "none";
        }
    });
}

document.addEventListener("DOMContentLoaded", initializePopup);

function startSim() {
    window.showPopup();
}

function runAISimulation() {
    generateRewardSystem();
    runQLearning();
}

function generateRewardSystem() {
    const rewardGrid = [];
    const endRow = parseInt(window.endSquare.dataset.row);
    const endCol = parseInt(window.endSquare.dataset.col);
    const maxDistance = Math.sqrt(Math.pow(window.ROWS - 1, 2) + Math.pow(window.COLS - 1, 2));

    // Initialize reward grid based on distance from end state
    for (let i = 0; i < window.ROWS; i++) {
        rewardGrid[i] = [];
        for (let j = 0; j < window.COLS; j++) {
            const distance = Math.sqrt(Math.pow(i - endRow, 2) + Math.pow(j - endCol, 2));
            const normalizedDistance = distance / maxDistance;
            rewardGrid[i][j] = Math.exp(-5 * normalizedDistance) - 0.5;
        }
    }

    // Set a much higher reward for the end square
    rewardGrid[endRow][endCol] = 100;

    // Adjust rewards for squares adjacent to walls
    const walls = getWalls();
    walls.forEach(wall => {
        const { row, col, orientation } = wall;

        // Adjust rewards for squares adjacent to horizontal walls
        if (orientation === 'horizontal') {
            if (row > 0) rewardGrid[row - 1][col] -= 0.1; // above the wall
            if (row < window.ROWS - 1) rewardGrid[row + 1][col] -= 0.1; // below the wall
        }

        // Adjust rewards for squares adjacent to vertical walls
        if (orientation === 'vertical') {
            if (col > 0) rewardGrid[row][col - 1] -= 0.1; // left of the wall
            if (col < window.COLS - 1) rewardGrid[row][col + 1] -= 0.1; // right of the wall
        }
    });

    console.log("Generated Reward Grid:", rewardGrid);
    return rewardGrid;
}

function getWalls() {
    const walls = [];
    document.querySelectorAll('.wall-space.wall').forEach(wallSpace => {
        const row = parseInt(wallSpace.dataset.row);
        const col = parseInt(wallSpace.dataset.col);
        const orientation = wallSpace.classList.contains('horizontal') ? 'horizontal' : 'vertical';
        walls.push({ row, col, orientation });
    });
    return walls;
}


class QLearningAgent {
    constructor(env, alpha = 0.1, gamma = 0.99, epsilon = 0.1) {
        this.env = env;
        this.alpha = alpha;
        this.gamma = gamma;
        this.epsilon = epsilon;
        this.qtable = this.initializeQTable();
    }

    initializeQTable() {
        const table = {};
        for (let i = 0; i < window.ROWS; i++) {
            for (let j = 0; j < window.COLS; j++) {
                const state = `${i},${j}`;
                table[state] = {
                    up: 0,
                    down: 0,
                    left: 0,
                    right: 0
                };
            }
        }
        return table;
    }

    chooseAction(state) {
        const validActions = this.env.getValidActions(state);
        if (Math.random() < this.epsilon) {
            return validActions[Math.floor(Math.random() * validActions.length)];
        } else {
            const stateActions = this.qtable[state];
            return validActions.reduce((a, b) => stateActions[a] > stateActions[b] ? a : b);
        }
    }

    learn(state, action, reward, nextState) {
        const predict = this.qtable[state][action];
        const validNextActions = this.env.getValidActions(nextState);
        const nextStateValues = validNextActions.map(a => this.qtable[nextState][a]);
        const target = reward + this.gamma * Math.max(...nextStateValues);
        this.qtable[state][action] += this.alpha * (target - predict);
    }
}

/*-----------simulates the environment in which the agent operates, providing states, rewards, and transitions based on the actions taken by the agent.-----------*/
class Environment {
    constructor(rewardGrid) {
        this.rewardGrid = rewardGrid;
        this.currentState = this.getStartState();
        this.endState = this.getEndState();
        this.walls = this.getWalls();

        console.log("Reward Grid:", this.rewardGrid);
        console.log("Start State:", this.currentState);
        console.log("End State:", this.endState);
        console.log("Walls:", this.walls);
    }

    getStartState() {
        const startRow = parseInt(window.startSquare.dataset.row);
        const startCol = parseInt(window.startSquare.dataset.col);
        return `${startRow},${startCol}`;
    }

    getEndState() {
        const endRow = parseInt(window.endSquare.dataset.row);
        const endCol = parseInt(window.endSquare.dataset.col);
        return `${endRow},${endCol}`;
    }

    getWalls() {
        const walls = new Set();
        document.querySelectorAll('.wall-space.wall').forEach(wallSpace => {
            const row = parseInt(wallSpace.dataset.row);
            const col = parseInt(wallSpace.dataset.col);
            const orientation = wallSpace.classList.contains('horizontal') ? 'h' : 'v';
            walls.add(`${row},${col},${orientation}`);
        });
        return walls;
    }

    reset() {
        this.currentState = this.getStartState();
        return this.currentState;
    }

    step(action) {
        const [row, col] = this.currentState.split(',').map(Number);
        let newRow = row;
        let newCol = col;

        switch (action) {
            case 'up': newRow--; break;
            case 'down': newRow++; break;
            case 'left': newCol--; break;
            case 'right': newCol++; break;
        }

        if (this.isValidMove(row, col, newRow, newCol)) {
            this.currentState = `${newRow},${newCol}`;
            const reward = this.rewardGrid[newRow][newCol];
            const done = this.currentState === this.endState;
            const finalReward = done ? reward + 1000 : reward;
            return [this.currentState, finalReward, done];
        } else {
            // If move is invalid, stay in the current state and apply a large penalty
            return [this.currentState, -1000, false];
        }
    }

    isValidMove(row, col, newRow, newCol) {
        if (newRow < 0 || newRow >= window.ROWS || newCol < 0 || newCol >= window.COLS) {
            return false;
        }

        // Check for walls
        if (row !== newRow) {  // Vertical movement
            const minRow = Math.min(row, newRow);
            if (this.walls.has(`${minRow},${col},h`)) return false;
        } else if (col !== newCol) {  // Horizontal movement
            const minCol = Math.min(col, newCol);
            if (this.walls.has(`${row},${minCol},v`)) return false;
        }

        return true;
    }

    getValidActions(state) {
        const [row, col] = state.split(',').map(Number);
        const validActions = [];
        if (this.isValidMove(row, col, row-1, col)) validActions.push('up');
        if (this.isValidMove(row, col, row+1, col)) validActions.push('down');
        if (this.isValidMove(row, col, row, col-1)) validActions.push('left');
        if (this.isValidMove(row, col, row, col+1)) validActions.push('right');
        return validActions;
    }
}

function runQLearning() {
    const rewardGrid = generateRewardSystem();
    console.log("Reward Grid in runQLearning:", rewardGrid);
    const env = new Environment(rewardGrid);
    const agent = new QLearningAgent(env);

    const numEpisodes = 10000;  // Increase the number of episodes
    const maxSteps = window.ROWS * window.COLS * 4;

    for (let episode = 0; episode < numEpisodes; episode++) {
        let state = env.reset();
        let totalReward = 0;
        
        for (let step = 0; step < maxSteps; step++) {
            const action = agent.chooseAction(state);
            const [nextState, reward, done] = env.step(action);
            agent.learn(state, action, reward, nextState);
            state = nextState;
            totalReward += reward;
            
            if (done) {
                console.log(`Episode ${episode + 1} finished after ${step + 1} steps. Total reward: ${totalReward}`);
                break;
            }
        }
        
        // Decay epsilon over time to reduce exploration
        agent.epsilon = Math.max(0.01, agent.epsilon * 0.9999);
    }

    showTrainingCompletePopup();
    displayOptimalPath(agent);
}

function showTrainingCompletePopup() {
    const popup = document.getElementById("popup");
    popup.textContent = 'Training complete!';
    popup.style.transform = 'translate(0%, 525%)'; 
    popup.style.opacity = '1';
    setTimeout(() => popup.remove(), 2000);
}

function displayOptimalPath(agent) {
    let state = agent.env.getStartState();
    const path = [state];
    const maxPathLength = window.ROWS * window.COLS * 2;
    let stepCount = 0;

    while (state !== agent.env.endState && stepCount < maxPathLength) {
        const validActions = agent.env.getValidActions(state);
        if (validActions.length === 0) {
            console.log("No valid moves available, stopping path");
            break;
        }

        const action = validActions.reduce((a, b) => agent.qtable[state][a] > agent.qtable[state][b] ? a : b);
        const [newRow, newCol] = state.split(',').map(Number);
        let nextRow = newRow;
        let nextCol = newCol;

        switch (action) {
            case 'up': nextRow--; break;
            case 'down': nextRow++; break;
            case 'left': nextCol--; break;
            case 'right': nextCol++; break;
        }

        state = `${nextRow},${nextCol}`;
        path.push(state);
        stepCount++;

        if (state === agent.env.endState) {
            console.log("End state reached!");
            break;
        }
    }

    console.log("Final path:", path);

    if (stepCount >= maxPathLength) {
        console.log("Maximum path length reached, path may be incomplete");
    }

    // Display the path
    path.forEach((state, index) => {
        const [row, col] = state.split(',').map(Number);
        const cell = document.querySelector(`.grid-cell[data-row="${row}"][data-col="${col}"]`);
        if (cell) {
            const pathMarker = document.createElement('div');
            pathMarker.className = 'path-marker';
            pathMarker.style.cssText = `
                width: 10px; 
                height: 10px; 
                background: ${index === 0 ? 'green' : index === path.length - 1 ? 'red' : 'blue'}; 
                border-radius: 50%; 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%);
            `;
            cell.appendChild(pathMarker);
        }
    });
}