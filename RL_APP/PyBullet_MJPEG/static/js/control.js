document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('startButton').addEventListener('click', startSimulation);
});

function startSimulation() {
    fetch('/start_simulation', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Simulation started');
            } else {
                console.error('Failed to start simulation:', data);
            }
        })
        .catch(error => console.error('Error starting simulation:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    let angle = 0;
    const maxAngle = Math.PI / 1; // 90 degrees in radians

    // Throttle function to limit the rate of setAngle calls
    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    const throttledSetAngle = throttle(setAngle, 200); // Adjust the limit as needed (200ms here)

    document.addEventListener('keydown', (event) => {
        switch(event.key) {
            case 'ArrowLeft':
                angle = -maxAngle;
                throttledSetAngle(angle);
                break;
            case 'ArrowRight':
                angle = maxAngle;
                throttledSetAngle(angle);
                break;
            case 'ArrowUp':
                angle = 0;  // Reset angle
                throttledSetAngle(angle);
                break;
            case 'ArrowDown':
                // Do nothing to freeze the angle
                console.log(`Angle frozen at ${angle} radians`);
                break;
            default:
                return; // Ignore other keys
        }
    });

    function setAngle(angle) {
        fetch(`/set_angle/${angle}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log(`Angle set to ${angle} radians`);
            } else {
                console.error('Failed to set angle:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
});
