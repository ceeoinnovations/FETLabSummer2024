import pybullet as p
import pybullet_data
import time
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

def run_pybullet_simulation(control_queue, initial_ball_position=[0.7, 0, 0.6]):
    try:
        physicsClient = p.connect(p.GUI)
        if physicsClient < 0:
            logging.error("Unable to connect to PyBullet server")
            return
        
        logging.info(f"Connected to PyBullet with connection ID: {physicsClient}")
        
        p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        p.resetDebugVisualizerCamera(cameraDistance=1.3, cameraYaw=180, cameraPitch=-15, cameraTargetPosition=[0, 0, 0.5])
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)
        p.setRealTimeSimulation(1)
        
        planeId = p.loadURDF("plane.urdf")
        ballbeam = p.loadURDF("resources/ballbeam/ballbeam.urdf", [0, 0, 0.5], useFixedBase=True)
        
        beam_length = 1.0  # Total length of the beam
        beam_height = 1.25
        ball_x = (initial_ball_position[0] - 0.5) * beam_length
        ball_y = initial_ball_position[1]
        ball_z = beam_height + 0.1
        
        ball = p.loadURDF("resources/ball/ball.urdf", [ball_x, ball_y, ball_z])
        blue_line_id = p.addUserDebugLine([0, 0, beam_height], [0, 0, beam_height + 0.1], [0, 0, 1], lineWidth=3)
        
        logging.info(f"Loaded plane ID: {planeId}, ballbeam ID: {ballbeam}, ball ID: {ball}")
        
        blue_line_position = 0.5  # Center of the beam initially
        line_x = (blue_line_position - 0.5) * beam_length  # Initialize line_x
        running = True
        update_counter = 0
        update_frequency = 10  # Update every 10 iterations

        # For stationary check
        stationary_counter = 0
        stationary_threshold = 60  # Number of updates required to consider it stationary

        def get_ball_position():
            ball_translation, _ = p.getBasePositionAndOrientation(ball)
            position = (ball_translation[0] + (beam_length / 2)) / beam_length  # Normalize to [0, 1]
            return position

        while running and p.isConnected():
            # Process messages from the control queue
            while not control_queue.empty():
                message = control_queue.get()
                if message == 'stop':
                    running = False
                elif isinstance(message, tuple):
                    if message[0] == 'set_angle':
                        angle = message[1]
                        p.setJointMotorControl2(ballbeam, 1, p.POSITION_CONTROL, targetPosition=angle, force=1000)
                    elif message[0] == 'set_ball_position':
                        ball_x = max(-beam_length / 2, min(beam_length / 2, (message[1] - 0.5) * beam_length))
                        p.resetBasePositionAndOrientation(ball, [ball_x, ball_y, beam_height + 0.1], [0, 0, 0, 1])
                    elif message[0] == 'set_blue_line_position':
                        blue_line_position = message[1]
                        line_x = (blue_line_position - 0.5) * beam_length  # Update line_x with new blue line position
                        p.addUserDebugLine([line_x, 0, beam_height], [line_x, 0, beam_height + 0.1], [0, 0, 1], lineWidth=3, replaceItemUniqueId=blue_line_id)
            
            if update_counter % update_frequency == 0:
                ball_pos = get_ball_position()
                if abs(ball_pos - blue_line_position) < 0.05:
                    stationary_counter += 1
                    if stationary_counter >= stationary_threshold:
                        reward = 100  # Reward for staying aligned
                    else:
                        reward = 0  # Not rewarding yet, waiting for the stationary threshold
                else:
                    stationary_counter = 0  # Reset counter if out of alignment
                    reward = -1  # Penalize for not being aligned

                control_queue.put(('positions', {
                    'ball': ball_pos,
                    'blue_line': blue_line_position,
                    'reward': reward
                }))

                # Add a less distracting debug line from the beam to the ball
                line_from = [0, 0, beam_height]  # Beam's base position (pivot point)
                ball_translation, _ = p.getBasePositionAndOrientation(ball)
                line_to = [ball_translation[0], ball_translation[1], ball_translation[2]]
                p.addUserDebugLine(line_from, line_to, [0.7, 0.7, 0.7], lineWidth=1, lifeTime=1)  # Light grey line
        
            update_counter += 1
            time.sleep(1/240)
        
    except Exception as e:
        logging.error(f"An error occurred in the PyBullet simulation: {str(e)}")
    finally:
        if p.isConnected():
            p.disconnect()
            logging.info("Disconnected from PyBullet")
