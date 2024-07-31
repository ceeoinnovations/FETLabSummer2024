# PyBullet Simulation Web Application

This application integrates the PyBullet simulation engine with a Flask web server, allowing users to control simulations, view results, and compare outcomes directly from a web interface.

## Features

- **PyBullet Simulation**: Run and interact with simulations using the PyBullet physics engine.
- **Real-time Control**: Adjust simulation parameters such as beam angle and ball position.
- **Result Tracking**: Store and view results from various simulation runs.
- **Comparison**: Compare results to analyze different simulation outcomes.

## Getting Started

### Prerequisites

- **Python 3.11.9**

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask Server**:
   ```bash
   python app.py
   ```
   The app will run on `http://127.0.0.1:5000/` by default.

2. **Access the Application**:
   Open your web browser and navigate to `http://127.0.0.1:5000/` to interact with the simulation interface.

## Components

### 1. `app.py`

**Description:**  
This is the main Flask application file.

**Responsibilities:**
- Sets up the Flask web server.
- Defines routes for various functionalities, including:
  - **Home Page (`/`)**: Main landing page.
  - **New Training (`/new_training`)**: Interface for starting new training sessions.
  - **View All Results (`/view_all_results`)**: Displays results from previous simulations.
  - **Play Mode (`/play`)**: Interface for simulation control.
  - **Start Simulation (`/start_simulation`)**: Starts the PyBullet simulation.
  - **Stop Simulation (`/stop_simulation`)**: Stops the PyBullet simulation.
  - **Reset Simulation (`/reset_simulation`)**: Resets the simulation state.
  - **Set Angle (`/set_angle`)**: Sets the angle of the beam in the simulation.
  - **Set Ball Position (`/set_ball_position`)**: Sets the position of the ball on the beam.
  - **Set Blue Line Position (`/set_blue_line_position`)**: Sets the position of a reference line in the simulation.
  - **Compare Results (`/compare_results`)**: Compares results from different simulation runs.

### 2. `pybullet_sim.py`

**Description:**  
This script contains the PyBullet simulation logic.

**Responsibilities:**
- Manages the physics simulation of the ball-and-beam system.
- Sets up the simulation environment and loads models.
- Processes control commands from the web application to manage simulation state.
- Streams real-time simulation data to the web interface.

## Technologies Used

- **PyBullet**: Physics simulation library.
- **Flask**: Web framework for building the server-side application.
- **Jinja2**: Template engine for rendering HTML.

## How It Works

- **Simulation**: Runs in a separate thread and controls the ball-and-beam system.
- **Control**: Simulation parameters can be adjusted via the web interface, and commands are processed using message queues.
- **Data Streaming**: Real-time data from the simulation, including position and reward information, is streamed to the web application for visualization.
