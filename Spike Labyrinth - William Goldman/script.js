document.addEventListener('DOMContentLoaded', function() {
    window.ROWS = 5;
    window.COLS = 5;
    let walls = [];
    let nodes = [];
    let gridRotation = 0;
    let rotationDirection = '';
    window.startSquare = null;
    window.endSquare = null;
    let isSelectingStart = false;
    let isSelectingEnd = false;
    window.simStarted = false;
    window.gameStarted = false;

    const ctx = setupCanvas();
    const CANVAS_WIDTH = ctx.canvas.width;
    const CANVAS_HEIGHT = ctx.canvas.height;
    const BALL_RADIUS = 25;
    let ballX = CANVAS_WIDTH / 2;
    let ballY = CANVAS_HEIGHT / 2;
    let ballRotation = 0;
    let velocityX = 0;
    let velocityY = 0;
    let lastPitch = 0;
    let lastRoll = 0;
    let pitch = 0;
    let roll = 0;

    const GRAVITY = 9.81;
    const FRICTION = 0.83; // reversed: 1 is no friction, 0 is all friction
    const MIN_TILT_ANGLE = 0.005; // minimum tilt angle to overcome static friction (in radians)
    const RESTITUTION = 0.9; // bouncing off wall amount

    window.ballControlMode = 'coordinates';

//--------------------------------- Basic Helper Functions ---------------------------------

    function setupCanvas() {
        const canvas = document.getElementById('animationCanvas');
        const simulation = document.getElementById('simulation');
        canvas.width = simulation.offsetWidth;
        canvas.height = simulation.offsetHeight;
        return canvas.getContext('2d');
    }

    function unrotateCoordinates(row, col) {
        switch(gridRotation) {
            case 0: return [row, col];
            case 90: return [window.COLS - 1 - col, row];
            case 180: return [window.ROWS - 1 - row, window.COLS - 1 - col];
            case 270: return [col, window.ROWS - 1 - row];
        }
    }

    function promptUser(message) {
        document.getElementById('update-text').innerHTML = message;
    }

    function handleSquareClick(event) {
        const square = event.target;
        if (isSelectingStart) {
            setStartSquare(square);
        } else if (isSelectingEnd) {
            setEndSquare(square);
        }
    }

    //map a value from one range to another: this formula normalizes the input value to a 0-1 range based on inMin and inMax, 
    //then scales it to the output range based on outMin and outMax, and finally shifts it to the correct position within the output range.
    //ex: [10, 20] on the range [0, 100]. for input of '15', it would be (15 - 10) * (100 - 0) / (20 - 10) + 0 = 50
    function mapRange(value, inMin, inMax, outMin, outMax) {
        return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
    }

//--------------------------------- Initialize game: start & end square, ball init, game end condition ---------------------------------

    function initializeGame() {
        window.startSquare = null;
        window.endSquare = null;
        isSelectingStart = true;
        isSelectingEnd = false;
        window.gameStarted = false;
        window.simStarted = false;
        promptUser("Select the start square and draw labyrinth walls");
    }
    
    function setStartSquare(square) {
        if (window.startSquare) {
            window.startSquare.classList.remove('start');
            window.startSquare.textContent = '';
        }
        window.startSquare = square;
        window.startSquare.classList.add('start');
        window.startSquare.textContent = 'Start';
        isSelectingStart = false;
        isSelectingEnd = true;
        promptUser("Select the end square");
    }

    function setEndSquare(square) {
        if (window.endSquare) {
            window.endSquare.classList.remove('end');
            window.endSquare.textContent = '';
        }
        window.endSquare = square;
        window.endSquare.classList.add('end');
        window.endSquare.textContent = 'End';
        isSelectingEnd = false;
        promptUser("Move the ball to the end square");
        initializeBall();
    }
    
    function initializeBall() {
        const cellWidth = CANVAS_WIDTH / window.COLS;
        const cellHeight = CANVAS_HEIGHT / window.ROWS;
        const [startRow, startCol] = unrotateCoordinates(parseInt(window.startSquare.dataset.row), parseInt(window.startSquare.dataset.col));
        ballX = (startCol + 0.5) * cellWidth;
        ballY = (startRow + 0.5) * cellHeight;
        velocityX = 0;
        velocityY = 0;
        ballRotation = 0;
        window.simStarted = true;
        animate();
    }
    
    function checkEndReached() {
        const cellWidth = CANVAS_WIDTH / window.COLS;
        const cellHeight = CANVAS_HEIGHT / window.ROWS;
        const [endRow, endCol] = unrotateCoordinates(parseInt(window.endSquare.dataset.row), parseInt(window.endSquare.dataset.col));
        const endX = (endCol + 0.5) * cellWidth;
        const endY = (endRow + 0.5) * cellHeight;
        
        const distance = Math.sqrt(Math.pow(ballX - endX, 2) + Math.pow(ballY - endY, 2));
        if (distance < BALL_RADIUS * 2) {
            promptUser("Goal reached! Restarting the game.");
            window.startSquare.classList.remove('start');
            window.startSquare.textContent = '';
            window.endSquare.classList.remove('end');
            window.endSquare.textContent = '';
            initializeGame();
        }
    }

//----------------------------------------------- Grid and Node Setup ------------------------------------------------

    function createGrid(rows, cols) {
        const gridContainer = document.getElementById('grid-container');
        gridContainer.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
        gridContainer.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                const cell = document.createElement('div');
                cell.classList.add('grid-cell');
                cell.dataset.row = i;
                cell.dataset.col = j;
                cell.addEventListener('click', handleSquareClick);
    
                // Add wall spaces
                if (i > 0) {
                    const horizontalWall = document.createElement('div');
                    horizontalWall.classList.add('wall-space', 'horizontal');
                    horizontalWall.dataset.row = i;
                    horizontalWall.dataset.col = j;
                    horizontalWall.dataset.orientation = 'horizontal';
                    horizontalWall.addEventListener('click', toggleWall);
                    cell.appendChild(horizontalWall);
                }
                if (j > 0) {
                    const verticalWall = document.createElement('div');
                    verticalWall.classList.add('wall-space', 'vertical');
                    verticalWall.dataset.row = i;
                    verticalWall.dataset.col = j;
                    verticalWall.dataset.orientation = 'vertical';
                    verticalWall.addEventListener('click', toggleWall);
                    cell.appendChild(verticalWall);
                }
    
                gridContainer.appendChild(cell);
            }
        }
        createNodes(gridContainer, rows, cols);
    }
    
    function createNodes(gridContainer, rows, cols) {
        for (let i = 0; i <= rows; i++) {
            for (let j = 0; j <= cols; j++) {
                const node = document.createElement('div');
                
                // remove nodes from corners
                if (!((i === 0 && j ===0) || (i === 0 && j === cols) || (i === rows && j === 0) || (i === rows && j === cols))) {
                    node.classList.add('grid-node');
                    updateNodePosition(node, i, j);
                }

                gridContainer.appendChild(node);
            }
        }
    }

    function toggleWall(event) {
        event.stopPropagation();
        const wallSpace = event.target;
        wallSpace.classList.toggle('wall');
        updateWalls();
    }

    function updateWalls() {
        document.querySelectorAll('.wall-space.wall').forEach(wallSpace => {
            const row = parseInt(wallSpace.dataset.row);
            const col = parseInt(wallSpace.dataset.col);
            const orientation = wallSpace.dataset.orientation;
    
            if (orientation === 'horizontal') {
                walls.push({
                    x1: col, y1: row,
                    x2: col + 1, y2: row
                });
            } else {
                walls.push({
                    x1: col, y1: row,
                    x2: col, y2: row + 1
                });
            }
        });
    }

    function updateNodePosition(node, row, col) {
        node.style.gridRow = row + 1;
        node.style.gridColumn = col + 1;
        node.dataset.row = row;
        node.dataset.col = col;
    }

    function checkForWalls(node) {
        const row = parseInt(node.dataset.row);
        const col = parseInt(node.dataset.col);
        
        const directions = [
            {dr: 0, dc: 1}, // right
            {dr: 1, dc: 0}, // down
            {dr: 0, dc: -1}, // left
            {dr: -1, dc: 0}  // up
        ];
        
        directions.forEach(dir => { // wall handler
            const neighborRow = row + dir.dr;
            const neighborCol = col + dir.dc;
            const neighbor = document.querySelector(`.grid-node[data-row="${neighborRow}"][data-col="${neighborCol}"]`);
            
            if (neighbor && neighbor.classList.contains('selected')) {
                if (node.classList.contains('selected')) {
                    addWall(row, col, neighborRow, neighborCol);
                } else {
                    removeWall(row, col, neighborRow, neighborCol);
                }
            }
        });
    }

    function addWall(row1, col1, row2, col2) {
        const newWall = {x1: col1, y1: row1, x2: col2, y2: row2};
        if (!walls.some(wall => // tests whether at least one element in the array passes the test implemented by the provided function (true or false)
            (wall.x1 === newWall.x1 && wall.y1 === newWall.y1 && wall.x2 === newWall.x2 && wall.y2 === newWall.y2) ||
            (wall.x1 === newWall.x2 && wall.y1 === newWall.y2 && wall.x2 === newWall.x1 && wall.y2 === newWall.y1)
        )) {
            walls.push(newWall);
        }
    }

    function removeWall(row1, col1, row2, col2) {
        walls = walls.filter(wall => // creates a new array with all elements that pass the test implemented by the provided function
            !(wall.x1 === col1 && wall.y1 === row1 && wall.x2 === col2 && wall.y2 === row2) &&
            !(wall.x1 === col2 && wall.y1 === row2 && wall.x2 === col1 && wall.y2 === row1)
        );
    }

//--------------------------------- Rotate Grid counterclockwise or clockwise ---------------------------------

    function rotateGrid(direction) {
        if (direction === 'cw') {
            gridRotation = (gridRotation + 90) % 360;
            rotationDirection = 'cw';
        } else {
            gridRotation = (gridRotation - 90 + 360) % 360;
            rotationDirection = 'ccw';
        }
        updateDirectionIndicator();
        rotateWalls();
        rotateStartEndSquares();
        redrawCanvas();
    }

    function rotateCoordinates(row, col, gridSize) { 
        if (rotationDirection === 'cw') {
            return [col, gridSize - 1 - row]; //rotates coordinates 90 degrees clockwise
        }
        else{
            return [gridSize - 1 - col, row]; //rotates coordinates 90 degrees counterclockwise
        }
    }

    function rotateWalls() {
        const gridContainer = document.getElementById('grid-container');
        const wallSpaces = gridContainer.querySelectorAll('.wall-space.wall');
        const gridSize = 5;

        // Store current wall elements and their data
        const wallsData = [];
        wallSpaces.forEach(wallSpace => {
            const oldRow = parseInt(wallSpace.dataset.row);
            const oldCol = parseInt(wallSpace.dataset.col);
            const oldOrientation = wallSpace.dataset.orientation;
            wallsData.push({ element: wallSpace, row: oldRow, col: oldCol, orientation: oldOrientation });
        });
    
        // Remove all current wall elements
        wallSpaces.forEach(wallSpace => wallSpace.remove());
    
        // Recreate wall elements with updated positions and orientations
        wallsData.forEach(wall => {
            let [newRow, newCol] = rotateCoordinates(wall.row, wall.col, gridSize);
            let newOrientation = wall.orientation === 'horizontal' ? 'vertical' : 'horizontal';
            
            // Create a new wall element
            const newWallSpace = document.createElement('div');
            newWallSpace.classList.add('wall-segment', newOrientation);
            newWallSpace.dataset.row = newRow;
            newWallSpace.dataset.col = newCol;
            newWallSpace.dataset.orientation = newOrientation;
            
            // Append new wall element to the grid
            gridContainer.appendChild(newWallSpace);
        });
    
        updateWalls();
    }

    function rotateStartEndSquares() {
        const gridSize = window.ROWS; // Assuming window.ROWS === window.COLS, otherwise use Math.max(window.ROWS, window.COLS)
    
        if (startSquare) {
            const [newRow, newCol] = rotateCoordinates(
                parseInt(window.startSquare.dataset.row),
                parseInt(window.startSquare.dataset.col),
                gridSize
            );
            console.log('Rotating start square:', window.startSquare.dataset.row, window.startSquare.dataset.col, '->', newRow, newCol);
            window.startSquare.classList.remove('start');
            window.startSquare.textContent = '';
            window.startSquare = document.querySelector(`.grid-cell[data-row="${newRow}"][data-col="${newCol}"]`);
            window.startSquare.classList.add('start');
            window.startSquare.textContent = 'Start';
        }
        if (window.endSquare) {
            const [newRow, newCol] = rotateCoordinates(
                parseInt(window.endSquare.dataset.row),
                parseInt(window.endSquare.dataset.col),
                gridSize
            );

            window.endSquare.classList.remove('end');
            window.endSquare.textContent = '';
            window.endSquare = document.querySelector(`.grid-cell[data-row="${newRow}"][data-col="${newCol}"]`);
            window.endSquare.classList.add('end');
            window.endSquare.textContent = 'End';
        }
    }
    
    function updateDirectionIndicator() {
        const indicator = document.getElementById('direction-indicator');
        indicator.innerHTML = ['↑', '→', '↓', '←'][gridRotation / 90];
    }


//----------------------------------------Canvas Setup/Drawing----------------------------------------

    function redrawCanvas() {
        ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        ctx.save();
        ctx.translate(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
        ctx.rotate(gridRotation * Math.PI / 180);
        ctx.translate(-CANVAS_WIDTH / 2, -CANVAS_HEIGHT / 2);
    
        drawGrid();
        drawWalls();
    
        ctx.restore();
    
        if (window.gameStarted) {
            if (window.ballControlMode === 'sensors'){
                moveCircle(lastPitch, lastRoll);
                drawTiltIndicator(pitch, roll);
            } else {
                drawBall(ballX, ballY);
            }
            checkEndReached();
        }
    }

    function drawGrid() {
        const cellWidth = CANVAS_WIDTH / window.COLS;
        const cellHeight = CANVAS_HEIGHT / window.ROWS;
    
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 1;
    
        for (let i = 0; i <= window.ROWS; i++) {
            ctx.beginPath();
            ctx.moveTo(0, i * cellHeight);
            ctx.lineTo(CANVAS_WIDTH, i * cellHeight);
            ctx.stroke();
        }
    
        for (let j = 0; j <= window.COLS; j++) {
            ctx.beginPath();
            ctx.moveTo(j * cellWidth, 0);
            ctx.lineTo(j * cellWidth, CANVAS_HEIGHT);
            ctx.stroke();
        }
    }

    function drawWalls() {
        ctx.strokeStyle = '#3d3b34';
        ctx.lineWidth = 6;
        const cellWidth = CANVAS_WIDTH / window.COLS;
        const cellHeight = CANVAS_HEIGHT / window.ROWS;
        
        walls.forEach(wall => {
            ctx.beginPath();
            ctx.moveTo(wall.x1 * cellWidth, wall.y1 * cellHeight);
            ctx.lineTo(wall.x2 * cellWidth, wall.y2 * cellHeight);
            ctx.stroke();
        });
    }

    //for my particular setup, the coordinates I am recieving from the openMV program need to be scaled to match the grid on the webpage to match my 'forward' direction
    //so here I define the OpenMV camera's coordinates for the grid corners (place the ball in each corner of the grid and see what the openMV cam registers)
    const cameraCorners = {
        bottomRight: { x: 267, y: 22 },
        topRight: { x: 267, y: 210 },
        topLeft: { x: 77, y: 210 },
        bottomLeft: { x: 77, y: 22 }
    };

    function drawBall(x, y) {
        const rotatedPoint = rotatePoint(x, y, -gridRotation);
        
        ctx.beginPath();
        ctx.arc(rotatedPoint.x, rotatedPoint.y, BALL_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = 'red';
        ctx.fill();

        const gradient = ctx.createRadialGradient(
            rotatedPoint.x - BALL_RADIUS / 3, rotatedPoint.y - BALL_RADIUS / 3, BALL_RADIUS / 10,
            rotatedPoint.x, rotatedPoint.y, BALL_RADIUS
        );
        gradient.addColorStop(0, 'white');
        gradient.addColorStop(1, 'red');
    
        ctx.beginPath();
        ctx.arc(rotatedPoint.x, rotatedPoint.y, BALL_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(rotatedPoint.x + Math.cos(ballRotation) * BALL_RADIUS / 2, 
                rotatedPoint.y + Math.sin(ballRotation) * BALL_RADIUS / 2, 
                BALL_RADIUS / 5, 0, Math.PI * 2);
        ctx.fillStyle = '#fcd3d2';
        ctx.fill();
    }

    function rotatePoint(x, y, angle) {
        const centerX = CANVAS_WIDTH / 2;
        const centerY = CANVAS_HEIGHT / 2;
        const radians = angle * Math.PI / 180;
        const cos = Math.cos(radians);
        const sin = Math.sin(radians);
        const nx = (cos * (x - centerX)) + (sin * (y - centerY)) + centerX;
        const ny = (cos * (y - centerY)) - (sin * (x - centerX)) + centerY;
        return { x: nx, y: ny };
    }

//--------------------------------- ball calculation for physics, call drawBall, and interaction on canvas ---------------------------------

    function moveCircle(pitch, roll) {
        if (!window.gameStarted) return; //prevent overriding the ball position

        ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

        // Adjust tilt based on grid rotation
        let adjustedPitch = pitch;
        let adjustedRoll = roll;
        switch(gridRotation) {
            case 90:
                adjustedPitch = roll;
                adjustedRoll = -pitch;
                break;
            case 180:
                adjustedPitch = -pitch;
                adjustedRoll = -roll;
                break;
            case 270:
                adjustedPitch = -roll;
                adjustedRoll = pitch;
                break;
        }

        let tiltX = Math.sin(adjustedRoll);
        let tiltY = Math.sin(adjustedPitch);
    
        let tiltMagnitude = Math.sqrt(tiltX * tiltX + tiltY * tiltY);
    
        // Check if tilt exceeds the minimum angle to overcome static friction
        if (tiltMagnitude > MIN_TILT_ANGLE) {
            let accX = rotatedTiltX * GRAVITY;
            let accY = rotatedTiltY * GRAVITY;
    
            velocityX += accX;
            velocityY += accY;
    
            velocityX *= FRICTION;
            velocityY *= FRICTION;
    
            let newX = ballX + velocityX;
            let newY = ballY + velocityY;
    
            // Check for wall collisions
            let collided = handleWallCollisions(newX, newY);
    
            // If no collision occurred, update ball position
            if (!collided) {
                ballX = newX;
                ballY = newY;
            }
    
            // Check for node collisions
            handleNodeCollisions(ballX, ballY);
    
            // Keep ball within canvas bounds (with bounce)
            handleBoundaryCollisions();
    
            const distanceMoved = Math.sqrt(velocityX * velocityX + velocityY * velocityY);
            ballRotation += distanceMoved / BALL_RADIUS;
    
            if (Math.abs(velocityX) < 0.01) velocityX = 0;
            if (Math.abs(velocityY) < 0.01) velocityY = 0;
        } 
        else {
            // Ball doesn't move due to static friction
            velocityX = 0;
            velocityY = 0;
        }
    }

    function handleWallCollisions(newX, newY) {
        const cellWidth = CANVAS_WIDTH / window.COLS;
        const cellHeight = CANVAS_HEIGHT / window.ROWS;
        let collided = false;
        
        walls.forEach(wall => {
            const x1 = wall.x1 * cellWidth;
            const y1 = wall.y1 * cellHeight;
            const x2 = wall.x2 * cellWidth;
            const y2 = wall.y2 * cellHeight;
            
            if (lineCircleCollision(x1, y1, x2, y2, newX, newY, BALL_RADIUS)) {
                collided = true;
                const wallVector = {x: x2 - x1, y: y2 - y1};
                const wallLength = Math.sqrt(wallVector.x * wallVector.x + wallVector.y * wallVector.y);
                const normal = {x: -wallVector.y / wallLength, y: wallVector.x / wallLength};
    
                // Calculate the dot product of velocity and normal
                const dot = velocityX * normal.x + velocityY * normal.y;
    
                // Apply restitution to the reflected velocity
                velocityX = (velocityX - 2 * dot * normal.x) * RESTITUTION;
                velocityY = (velocityY - 2 * dot * normal.y) * RESTITUTION;
    
                // Move the ball to just touch the wall
                const distanceToWall = distancePointToLine(ballX, ballY, x1, y1, x2, y2) - BALL_RADIUS;
                ballX -= distanceToWall * normal.x;
                ballY -= distanceToWall * normal.y;
            }
        });
    
        return collided;
    }

    function handleBoundaryCollisions() {
        if (ballX < BALL_RADIUS) {
            ballX = BALL_RADIUS;
            velocityX = -velocityX * RESTITUTION;
        } else if (ballX > CANVAS_WIDTH - BALL_RADIUS) {
            ballX = CANVAS_WIDTH - BALL_RADIUS;
            velocityX = -velocityX * RESTITUTION;
        }
    
        if (ballY < BALL_RADIUS) {
            ballY = BALL_RADIUS;
            velocityY = -velocityY * RESTITUTION;
        } else if (ballY > CANVAS_HEIGHT - BALL_RADIUS) {
            ballY = CANVAS_HEIGHT - BALL_RADIUS;
            velocityY = -velocityY * RESTITUTION;
        }
    }

    function lineCircleCollision(x1, y1, x2, y2, cx, cy, r) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const fx = x1 - cx;
        const fy = y1 - cy;
        const a = dx * dx + dy * dy;
        const b = 2 * (fx * dx + fy * dy);
        const c = (fx * fx + fy * fy) - r * r;
        const discriminant = b * b - 4 * a * c;
        
        if (discriminant < 0) {
            return false;
        }
        
        const t1 = (-b + Math.sqrt(discriminant)) / (2 * a);
        const t2 = (-b - Math.sqrt(discriminant)) / (2 * a);
        
        if ((0 <= t1 && t1 <= 1) || (0 <= t2 && t2 <= 1)) {
            return true;
        }
        
        return false;
    }

    function handleNodeCollisions(newX, newY) {
        nodes.forEach(node => {
            const dx = newX - node.x;
            const dy = newY - node.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < BALL_RADIUS + node.radius) {
                // Collision detected, calculate normal vector
                const normal = {x: dx / distance, y: dy / distance};

                // Calculate relative velocity
                const relativeVelocity = {x: velocityX, y: velocityY};

                // Calculate velocity along the normal
                const velocityAlongNormal = relativeVelocity.x * normal.x + relativeVelocity.y * normal.y;

                // Only resolve if objects are moving towards each other
                if (velocityAlongNormal < 0) {
                    // Calculate impulse scalar
                    const impulseScalar = -(1 + RESTITUTION) * velocityAlongNormal;

                    // Apply impulse
                    velocityX += impulseScalar * normal.x;
                    velocityY += impulseScalar * normal.y;

                    // Move the ball outside the node
                    const moveDistance = BALL_RADIUS + node.radius - distance;
                    ballX += moveDistance * normal.x;
                    ballY += moveDistance * normal.y;
                }
            }
        });
    }

    function closestPointOnLine(px, py, x1, y1, x2, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy);
        const clampedT = Math.max(0, Math.min(1, t));
        return {
            x: x1 + clampedT * dx,
            y: y1 + clampedT * dy
        };
    }
    
    function distancePointToLine(px, py, x1, y1, x2, y2) {
        const closest = closestPointOnLine(px, py, x1, y1, x2, y2);
        const dx = px - closest.x;
        const dy = py - closest.y;
        return Math.sqrt(dx * dx + dy * dy);
    }

//----------------------------------- Other canvas drawing -----------------------------------

    function drawTiltIndicator(pitch, roll) {
        const radius = BALL_RADIUS * 2;
        let tiltX = Math.sin(roll);
        let tiltY = Math.sin(pitch);
    
        // Adjust tilt direction based on grid rotation
        switch(gridRotation) {
            case 90:
                [tiltX, tiltY] = [-tiltY, tiltX];
                break;
            case 180:
                [tiltX, tiltY] = [-tiltX, -tiltY];
                break;
            case 270:
                [tiltX, tiltY] = [tiltY, -tiltX];
                break;
        }
    
        const rotatedBallPos = rotatePoint(ballX, ballY, -gridRotation);
    
        ctx.beginPath();
        ctx.moveTo(rotatedBallPos.x, rotatedBallPos.y);
        ctx.lineTo(rotatedBallPos.x + tiltX * radius, rotatedBallPos.y + tiltY * radius);
        ctx.strokeStyle = 'blue';
        ctx.lineWidth = 2;
        ctx.stroke();
    }

//--------------------------------- Event Listeners and Initialization -------------------------------

    //change the mode of the button beneath the grid: modes switch between x, y control and yaw, pitch, and roll control

    window.toggleBallControlMode = function() {
        const toggle = document.getElementById('toggleMode');
        const slider = toggle.querySelector('.slider');
        
        if (window.ballControlMode === 'sensors') {
            window.ballControlMode = 'coordinates';
            slider.style.transform = 'translateX(0)';
        } else {
            window.ballControlMode = 'sensors';
            slider.style.transform = 'translateX(-50%)';
        }
        
        console.log('Ball control mode switched to:', window.ballControlMode);
    
        // Notify Python about the mode change
        if (window.notifyPythonModeChange) {
            window.notifyPythonModeChange(window.ballControlMode);
        }
    };
    
    window.updateBallPosition = function(x, y) {
        if (window.ballControlMode === 'coordinates') {
            //map the camera coordinates to canvas coordinates
            const canvasX = mapRange(x, cameraCorners.topRight.x, cameraCorners.topLeft.x, 0, CANVAS_WIDTH);
            const canvasY = mapRange(y, cameraCorners.topLeft.y, cameraCorners.bottomLeft.y, 0, CANVAS_HEIGHT);

            //ensure the ball stays within the canvas boundaries
            ballX = Math.max(BALL_RADIUS, Math.min(CANVAS_WIDTH - BALL_RADIUS, canvasX));
            ballY = Math.max(BALL_RADIUS, Math.min(CANVAS_HEIGHT - BALL_RADIUS, canvasY));
        }
    };
    
    window.updateBallTilt = function(pitch, roll) {
        if (window.ballControlMode === 'sensors') {
            lastPitch = pitch;
            lastRoll = roll;
        }
    };

    document.getElementById('rotate-cw').addEventListener('click', () => rotateGrid('cw'));
    document.getElementById('rotate-ccw').addEventListener('click', () => rotateGrid('ccw'));

    createGrid(window.ROWS, window.COLS);
    
    // Animation Loop
    function animate() {
        if (window.simStarted){
            startSim() //this function in pathCalc.js
            simStarted = false;
        }
        redrawCanvas();
        requestAnimationFrame(animate);
    }

    initializeGame();
});