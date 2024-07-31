from flask import Flask, render_template, jsonify, Response
from queue import Queue, Empty
from threading import Thread
import cv2
import numpy as np
import pybullet as p
import pybullet_data
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Create queues for frames and control messages
frame_queue = Queue(maxsize=10)
control_queue = Queue(maxsize=10)

# Global variables
simulation_thread = None
current_angle = 0

def run_pybullet_simulation(frame_queue, control_queue):
    global current_angle
    try:
        # Connect to PyBullet in DIRECT mode (headless, no GUI)
        physicsClient = p.connect(p.DIRECT)
        if physicsClient < 0:
            logging.error("Unable to connect to PyBullet server")
            return
        
        logging.info(f"Connected to PyBullet with connection ID: {physicsClient}")
        
        # Configure the visualizer and set up the environment
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.68)
        p.setRealTimeSimulation(1)
        
        # Load URDF models for the plane and the beam
        planeId = p.loadURDF("plane.urdf")
        ballbeam = p.loadURDF("resources/ballbeam/ballbeam.urdf", [0, 0, 0.5], useFixedBase=True)
        
        # Define initial positions
        beam_length = 1.0
        beam_height = 1.25
        ball_x = -0.4
        ball_y = 0
        ball_z = 0.9
        
        # Load the ball model
        ball = p.loadURDF("resources/ball/ball.urdf", [ball_x, ball_y, ball_z])
        
        # Initialize the blue line
        
        logging.info(f"Loaded plane ID: {planeId}, ballbeam ID: {ballbeam}, ball ID: {ball}")
        
        # Simulation control variables
        running = True

        def get_ball_position():
            # Get the position and orientation of the ball
            ball_translation, _ = p.getBasePositionAndOrientation(ball)
            current_angle = p.getEulerFromQuaternion(p.getLinkState(ballbeam, 2)[1])[1]
            position = ball_translation[0]
            return position, current_angle

        # Ensure proper initialization
        for _ in range(10):
            p.stepSimulation()
            time.sleep(1/340)

        while running and p.isConnected():
            p.setJointMotorControl2(ballbeam, 1, p.POSITION_CONTROL, targetPosition=current_angle, force=1000)
            
            # Process messages from the control queue
            while not control_queue.empty():
                message = control_queue.get()
                if message == 'stop':
                    running = False
                elif isinstance(message, tuple):
                    if message[0] == 'set_angle':
                        current_angle = message[1]
                    
            # Get the position of the ball and the beam angle
            ball_pos, beam_angle = get_ball_position()
            
            # Put the positions into the control queue
            control_queue.put(('positions', {
                'ball': ball_pos,
                'beam_angle': beam_angle
            }))

            # Capture frame
            view_matrix = p.computeViewMatrix([0, -2, 1], [0, 0, 0.5], [0, 0, 1])
            projection_matrix = p.computeProjectionMatrixFOV(60, 640 / 360, 0.02, 10)
            _, _, rgbImg, _, _ = p.getCameraImage(640, 360, view_matrix, projection_matrix, shadow=True, renderer=p.ER_BULLET_HARDWARE_OPENGL)

            # Convert the captured image to a format suitable for streaming
            frame = np.reshape(rgbImg, (360, 640, 4))
            frame = frame[:, :, :3]

            # Put the frame into the queue
            if not frame_queue.full():
                frame_queue.put(frame)

            # Step simulation
            p.stepSimulation()

            # Sleep to maintain the simulation speed
            time.sleep(1/240)
        
    except Exception as e:
        logging.error(f"An error occurred in the PyBullet simulation: {str(e)}")
    finally:
        if p.isConnected():
            p.disconnect()
            logging.info("Disconnected from PyBullet")

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames():
    while True:
        frame = frame_queue.get()
        if isinstance(frame, np.ndarray):
            # Compress the frame to JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        # Yield each frame with the appropriate headers
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    global simulation_thread
    if simulation_thread is None or not simulation_thread.is_alive():
        # Start the simulation thread if not already running
        simulation_thread = Thread(target=run_pybullet_simulation, args=(frame_queue, control_queue))
        simulation_thread.start()
    return jsonify({'status': 'success'})

@app.route('/set_angle/<angle>', methods=['POST'])
def set_angle(angle):
    try:
        angle = float(angle)
        logging.info(f"Setting angle to: {angle}")
        control_queue.put(('set_angle', angle))
        return jsonify({'status': 'success'})
    except ValueError:
        logging.error(f"Invalid angle: {angle}")
        return jsonify({'status': 'error', 'message': 'Invalid angle'}), 400

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
