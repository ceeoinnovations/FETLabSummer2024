from flask import Flask, render_template, jsonify, request, Response
from queue import Queue
from threading import Thread, Lock
import logging
import json
import time
from pybullet_sim import run_pybullet_simulation

# Initialize Flask app and configure logging
app = Flask(__name__, static_folder='static')
logging.basicConfig(level=logging.INFO)

# Initialize a queue for communication with the PyBullet simulation
control_queue = Queue()

# A list to store results from the simulations
results = []

# Lock for thread-safe access to the results list
results_lock = Lock()

# Thread to run the PyBullet simulation
simulation_thread = None

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the new training page
@app.route('/new_training')
def new_training():
    return render_template('new_training.html')

# Route to view all results from simulations
@app.route('/view_all_results')
def view_all_results():
    with results_lock:
        message = None if results else "This is where results will be saved after you've run simulations."
        logging.info(f"Viewing all results. Total results: {len(results)}")
    return render_template('all_results.html', results=results, message=message)

# Route to run a training session
@app.route('/run_training', methods=['POST'])
def run_training():
    observations = sorted(request.form.getlist('observation'))
    logging.info(f"Selected observations: {observations}")
    time.sleep(4)  # Simulate processing time
    result = generate_result(observations)
    with results_lock:
        results.append(result)
    logging.info(f"Added result: {result}")
    return jsonify(result)

# Generate result data based on selected observations
def generate_result(observations):
    obs_map = {
        frozenset(['position']): 0,
        frozenset(['velocity']): 1,
        frozenset(['angle']): 2,
        frozenset(['position', 'velocity']): 3,
        frozenset(['position', 'angle']): 4,
        frozenset(['velocity', 'angle']): 5,
        frozenset(['position', 'velocity', 'angle']): 6
    }
    obs_set = frozenset(observations)
    obs_space_number = obs_map.get(obs_set, 0)
    return {
        'observations': observations,
        'obs_space_folder': f"OBS_SPACE_{obs_space_number}"
    }

# Route to view a specific training result
@app.route('/training_result')
def training_result():
    observations = request.args.getlist('observation')
    result = generate_result(observations)
    return render_template('training_result.html', result=result, obs_space_folder=result['obs_space_folder'])

# Route for play mode
@app.route('/play')
def play_mode():
    return render_template('play_mode.html')

# Route to start the PyBullet simulation
@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    global simulation_thread
    # Start a new simulation thread if one is not already running
    if simulation_thread is None or not simulation_thread.is_alive():
        logging.info("Starting new simulation thread")
        simulation_thread = Thread(target=run_pybullet_simulation, args=(control_queue,))
        simulation_thread.start()
    else:
        logging.info("Simulation thread already running")
    return jsonify({'status': 'success'})

# Route to stop the PyBullet simulation
@app.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    global simulation_thread
    # Stop the simulation thread if it is running
    if simulation_thread and simulation_thread.is_alive():
        control_queue.put('stop')
        simulation_thread.join()
        simulation_thread = None
    return '', 204

# Stream real-time position data from the simulation
@app.route('/get_positions')
def get_positions():
    def generate():
        while True:
            if not control_queue.empty():
                message = control_queue.get()
                if isinstance(message, tuple) and message[0] == 'positions':
                    yield f"data: {json.dumps(message[1])}\n\n"
            time.sleep(0.1)
    return Response(generate(), mimetype='text/event-stream')

# Route to reset the PyBullet simulation
@app.route('/reset_simulation', methods=['POST'])
def reset_simulation():
    global simulation_thread
    # Stop the current simulation and start a new one
    if simulation_thread and simulation_thread.is_alive():
        control_queue.put('stop')
        simulation_thread.join()
        simulation_thread = None
    # Clear the control queue and start a new simulation thread
    while not control_queue.empty():
        control_queue.get()
    simulation_thread = Thread(target=run_pybullet_simulation, args=(control_queue,))
    simulation_thread.start()
    return '', 204

# Route to set the angle of the beam in the simulation
@app.route('/set_angle', methods=['POST'])
def set_angle():
    angle = request.json.get('angle')
    if angle is not None and control_queue is not None:
        control_queue.put(('set_angle', angle))
    return '', 204

# Route to set the ball position in the simulation
@app.route('/set_ball_position/<float:position>', methods=['POST'])
def set_ball_position(position):
    if control_queue is not None:
        scaled_position = (position - 0.5) * 2
        control_queue.put(('set_ball_position', scaled_position))
    return '', 204

# Route to compare results from different simulations
@app.route('/compare_results')
def compare_results():
    items = []
    for key, value in request.args.items():
        if key.startswith('item'):
            items.append(json.loads(value))

    comparison_data = []
    with results_lock:
        for item in items:
            result = results[int(item['resultId'])]
            comparison_data.append({
                'observations': result['observations'],
                'obs_space_folder': result['obs_space_folder'],
                'type': item['type'],
                'filename': item['filename']
            })
    return render_template('compare_results.html', comparison_data=comparison_data)

# Route to set the blue line position in the simulation
@app.route('/set_blue_line_position/<float:position>', methods=['POST'])
def set_blue_line_position(position):
    if control_queue is not None:
        scaled_position = (position - 0.5) * 2
        control_queue.put(('set_blue_line_position', scaled_position))
    return '', 204

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, threaded=True)
