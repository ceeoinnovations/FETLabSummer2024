document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const startBtn = document.getElementById('start-btn'); // Start button
    const stopBtn = document.getElementById('stop-btn'); // Stop button
    const resetBtn = document.getElementById('reset-btn'); // Reset button
    const ballPositionSlider = document.getElementById('ball-position-slider'); // Slider for ball position
    const ballPositionValue = document.getElementById('ball-position-value'); // Display for ball position value
    const blueLinePositionSlider = document.getElementById('blue-line-position-slider'); // Slider for blue line position
    const blueLinePositionValue = document.getElementById('blue-line-position-value'); // Display for blue line position value
    const totalRewardDisplay = document.getElementById('total-reward-display'); // Display for total reward
    const modal = document.getElementById('instructionModal'); // Modal for instructions
    const startSimulationBtn = document.getElementById('startSimulationBtn'); // Button to start simulation
    const closeBtn = document.getElementsByClassName('close')[0]; // Button to close modal
    const helpModal = document.getElementById("helpModal"); // Help modal
    const helpBtn = document.getElementById("helpBtn"); // Help button

    // Initialize variables
    let cumulativeReward = 0;
    let dataPoints = 0;
    let eventSource;
    let startTime;
    let simulationRunning = false;
    let blueLinePosition = 0.5; // Initial position of blue line
    let currentAngle = 0; // Initial angle

    // Set up the graph using Chart.js
    const ctx = document.getElementById('rewardGraph').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [], // X-axis labels for time
            datasets: [{
                label: 'Reward', // Label for data
                data: [], // Data points for reward
                backgroundColor: function(context) { // Color based on value
                    const value = context.dataset.data[context.dataIndex];
                    return value >= 0 ? 'green' : 'red'; // Green for positive, red for negative rewards
                },
                borderColor: function(context) { // Border color same as background
                    return context.dataset.backgroundColor;
                },
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Time (s)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Reward'
                    },
                    ticks: {
                        beginAtZero: true // Start Y-axis at zero
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Reward Over Time',
                    font: {
                        size: 16
                    }
                },
                subtitle: {
                    display: true,
                    text: 'Positive rewards when aligned with the goal; penalties otherwise.',
                    font: {
                        size: 14
                    }
                },
                legend: {
                    labels: {
                        generateLabels: function(chart) { // Generate legend labels
                            let positiveRewards = false;
                            let negativeRewards = false;

                            chart.data.datasets[0].data.forEach((value) => {
                                if (value >= 0) positiveRewards = true;
                                else negativeRewards = true;
                            });

                            let labels = [];
                            if (positiveRewards) {
                                labels.push({
                                    text: 'Positive Reward',
                                    fillStyle: 'green',
                                    hidden: false,
                                    lineCap: 'butt',
                                    lineDash: [],
                                    lineDashOffset: 0,
                                    lineJoin: 'miter',
                                    lineWidth: 1,
                                    strokeStyle: 'green',
                                    pointStyle: 'rect',
                                    rotation: 0
                                });
                            }
                            if (negativeRewards) {
                                labels.push({
                                    text: 'Negative Reward',
                                    fillStyle: 'red',
                                    hidden: false,
                                    lineCap: 'butt',
                                    lineDash: [],
                                    lineDashOffset: 0,
                                    lineJoin: 'miter',
                                    lineWidth: 1,
                                    strokeStyle: 'red',
                                    pointStyle: 'rect',
                                    rotation: 0
                                });
                            }
                            return labels;
                        }
                    }
                }
            }
        }
    });

    // Event listeners for UI interactions
    startBtn.addEventListener('click', () => {
        fetch('/start_simulation', { method: 'POST' })
            .then(() => {
                modal.style.display = 'block';
            })
            .catch(error => console.error('Error starting simulation:', error));
    });

    startSimulationBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        startGraphAndEventSource(); // Start graph and data source
    });

    stopBtn.addEventListener('click', stopSimulation); // Stop simulation
    resetBtn.addEventListener('click', resetSimulation); // Reset simulation
    closeBtn.addEventListener('click', () => modal.style.display = 'none'); // Close modal
    ballPositionSlider.addEventListener('input', updateBallPosition); // Update ball position
    blueLinePositionSlider.addEventListener('input', updateBlueLinePosition); // Update blue line position
    window.addEventListener('resize', () => chart.resize()); // Resize chart on window resize
    document.addEventListener('keydown', handleKeyDown); // Handle keyboard input

    function startGraphAndEventSource() {
        if (!simulationRunning) {
            simulationRunning = true;
            startTime = Date.now();
            resetChart(); // Reset the chart
            startEventSource(); // Start receiving data
        }
    }

    function stopSimulation() {
        fetch('/stop_simulation', { method: 'POST' })
            .then(() => {
                simulationRunning = false;
                calculateAndDisplayTotalReward(); // Display total reward
                if (eventSource) eventSource.close();
            })
            .catch(error => console.error('Error stopping simulation:', error));
    }

    function resetSimulation() {
        fetch('/reset_simulation', { method: 'POST' })
            .then(() => {
                simulationRunning = false;
                ballPositionSlider.value = 0.5;
                ballPositionValue.textContent = '0.50';
                blueLinePositionSlider.value = 0.5;
                blueLinePositionValue.textContent = '0.50';
                cumulativeReward = 0;
                dataPoints = 0;
                totalRewardDisplay.innerText = '';
                resetChart(); // Reset the chart
                if (eventSource) eventSource.close();
            })
            .catch(error => console.error('Error resetting simulation:', error));
    }

    function updateChartData(currentTime, reward) {
        chart.data.labels.push(currentTime); // Add new time to labels
        chart.data.datasets[0].data.push(reward); // Add new reward to data

        // Ensure the chart is clear by limiting the number of bars
        const maxDataPoints = 200;
        if (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update();
    }

    function resetChart() {
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.update();
    }

    function startEventSource() {
        if (eventSource) {
            eventSource.close();
        }
        eventSource = new EventSource('/get_positions'); // Create a new EventSource
        eventSource.onmessage = handleEventMessage; // Handle incoming messages
    }

    let lastUpdateTime = 0;
    const updateInterval = 500; // Update every 500ms

    function handleEventMessage(event) {
        if (!simulationRunning) return;

        const now = Date.now();
        if (now - lastUpdateTime >= updateInterval) {
            const data = JSON.parse(event.data);
            const currentTime = (now - startTime) / 1000;
            updateChartData(currentTime, data.reward); // Update chart with new data
            updateCumulativeReward(data.reward); // Update cumulative reward
            lastUpdateTime = now;
        }
    }

    function updateCumulativeReward(instantReward) {
        cumulativeReward += instantReward; // Increment cumulative reward
        dataPoints++; // Increment data points count
    }

    function calculateAndDisplayTotalReward() {
        const averageReward = cumulativeReward / dataPoints; // Calculate average reward
        const totalReward = cumulativeReward.toFixed(2); // Total reward
        totalRewardDisplay.innerText = `
            Total Cumulative Reward: ${totalReward}
            Average Reward per Step: ${averageReward.toFixed(2)}
            Number of Steps: ${dataPoints}
        `;
    }

    function updateBallPosition() {
        const position = parseFloat(this.value); // Get slider value
        ballPositionValue.textContent = position.toFixed(2); // Update display value
        fetch(`/set_ball_position/${position}`, { method: 'POST' }) // Send new position to server
        .catch(error => console.error('Error setting ball position:', error));
    }

    function updateBlueLinePosition() {
        const position = parseFloat(this.value); // Get slider value
        blueLinePosition = position; // Update blue line position variable
        blueLinePositionValue.textContent = position.toFixed(2); // Update display value
        fetch(`/set_blue_line_position/${position}`, { method: 'POST' }) // Send new position to server
        .catch(error => console.error('Error setting blue line position:', error));
    }

    function handleKeyDown(event) {
        if (event.key === 'ArrowLeft') {
            currentAngle = Math.max(-0.2, currentAngle - 0.02); // Decrease angle with left arrow key
            setAngle(currentAngle);
        } else if (event.key === 'ArrowRight') {
            currentAngle = Math.min(0.2, currentAngle + 0.02); // Increase angle with right arrow key
            setAngle(currentAngle);
        }
    }

    function setAngle(angle) {
        fetch('/set_angle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ angle: angle }),
        })
        .catch(error => console.error('Error setting angle:', error));
    }

    window.addEventListener('beforeunload', function() {
        if (eventSource) eventSource.close(); // Close event source on page unload
    });
});
