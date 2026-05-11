# ROS2 Differential Drive TurtleBot Shape Drawer

A ROS2 Python project that demonstrates the fundamentals of:

- ROS2 Nodes
- Publishers and Subscribers
- Closed-loop control systems
- Differential drive robot logic
- Velocity control using `Twist`
- Pose feedback using `Pose`
- Path planning basics
- State machines
- Motion profiling with acceleration/deceleration

The robot draws polygon shapes inside `turtlesim` using closed-loop motion control.

This project is beginner-friendly and is designed to help understand how actual AMRs (Autonomous Mobile Robots) work internally.

---

# Table of Contents

1. Introduction
2. What is ROS2?
3. What is a Differential Drive Robot?
4. Open Loop vs Closed Loop Systems
5. Why Closed Loop is Used Here
6. ROS2 Concepts Demonstrated
7. Project Working Logic
8. Understanding the Code
9. Installing ROS2
10. Creating a ROS2 Workspace
11. Creating the Package
12. Writing the Node
13. Adding Dependencies
14. Updating `setup.py`
15. Building the Workspace
16. Running the Project
17. Expected Output
18. Important ROS2 Commands
19. Future Improvements
20. Conclusion

---

# 1. Introduction

This project controls the ROS2 `turtlesim` robot to draw polygon shapes automatically.

The robot:
- Reads its current pose continuously
- Calculates the next target point
- Moves forward
- Rotates precisely
- Repeats the process to form a polygon

Although this project uses `turtlesim`, the exact same concepts are used in:
- Warehouse AMRs
- Delivery robots
- Differential drive mobile robots
- AGVs
- Cleaning robots
- Service robots

---

# 2. What is ROS2?

ROS2 (Robot Operating System 2) is a robotics middleware framework.

It provides:
- Communication between robot components
- Hardware abstraction
- Message passing
- Real-time robot control
- Sensor integration
- Simulation support

ROS2 uses:
- Nodes
- Topics
- Publishers
- Subscribers
- Services
- Actions

This project mainly demonstrates:
- Nodes
- Publishers
- Subscribers
- Topics
- Timers

Official ROS2 Website:

https://docs.ros.org/

---

# 3. What is a Differential Drive Robot?

A differential drive robot has:
- Left wheel
- Right wheel

The robot moves by changing wheel speeds.

## Movement Logic

### Move Forward
Both wheels rotate at same speed.

### Turn Left
Right wheel rotates faster.

### Turn Right
Left wheel rotates faster.

### Rotate in Place
Wheels rotate in opposite directions.

---

# 4. Open Loop vs Closed Loop Systems

## Open Loop System

In an open loop system:
- No feedback is used
- System assumes motion happened correctly

Example:

```python
move_forward_for_5_seconds()
```

Problems:
- Wheel slip
- Drift
- No correction
- Poor accuracy

---

## Closed Loop System

In a closed loop system:
- Feedback is continuously monitored
- Errors are corrected automatically

Example:

```python
target_x - current_x
```

The robot constantly checks:
- Current position
- Current angle
- Velocity
- Distance remaining

Then adjusts speed accordingly.

---

# 5. Why Closed Loop is Used Here

This project uses a closed-loop control system because:

- Accurate shape drawing is required
- Robot must stop precisely
- Robot must rotate correctly
- Overshoot must be reduced

The turtle continuously receives pose feedback from:

```python
/turtle1/pose
```

Using this feedback:
- Distance error is calculated
- Angle error is calculated
- Speed is adjusted dynamically

This is similar to real AMRs using:
- Encoders
- IMUs
- LiDAR
- Odometry

---

# 6. ROS2 Concepts Demonstrated

# Node

A node is an executable process in ROS2.

This project creates a node called:

```python
turtle_shape
```

---

# Publisher

Publisher sends data to a topic.

This project publishes velocity commands:

```python
/turtle1/cmd_vel
```

Message type:

```python
geometry_msgs/Twist
```

---

# Subscriber

Subscriber receives data from a topic.

This project subscribes to:

```python
/turtle1/pose
```

Message type:

```python
turtlesim/Pose
```

---

# Topic

Topics are communication channels between nodes.

Example:

```text
Publisher --> Topic --> Subscriber
```

---

# Timer

The timer repeatedly executes the control loop.

```python
self.timer = self.create_timer(0.05, self.move_turtle)
```

This means:
- Function runs every 0.05 seconds
- Frequency = 20 Hz

---

# 7. Project Working Logic

The robot works using a simple state machine.

## States

### Idle
Robot reached target.

### Moving
Robot moves in straight line.

### Turning
Robot rotates to target angle.

---

# Workflow

## Step 1
Receive current pose from subscriber.

## Step 2
Calculate target coordinate.

## Step 3
Calculate:
- Distance error
- Angle error

## Step 4
If far from target:
- Move forward

## Step 5
If position reached:
- Rotate

## Step 6
Repeat to create polygon.

---

# 8. Understanding the Code

# Subscriber Creation

```python
self.subscription_= self.create_subscription(
    Pose,
    '/turtle1/pose',
    self.pose_callback,
    10
)
```

Receives turtle position continuously.

---

# Publisher Creation

```python
self.publisher_= self.create_publisher(
    Twist,
    '/turtle1/cmd_vel',
    10
)
```

Publishes velocity commands.

---

# Velocity Command

```python
cmd.linear.x
cmd.angular.z
```

These represent:
- Forward velocity
- Rotational velocity

---

# Error Calculation

```python
self.error_distance
self.error_theta
```

These are the core of closed-loop control.

---

# Motion Profiling

Acceleration and deceleration are implemented to:
- Avoid sudden jerks
- Reduce overshoot
- Simulate realistic motion

---

# State Machine Logic

```python
if(self.error_distance < self.threshold and self.error_theta < self.threshold_angle):
    self.state = "Idle"

elif(self.error_x < self.threshold and self.error_y < self.threshold and self.error_theta != 0):
    self.state = "Turning"

elif(self.error_distance != 0):
    self.state = "Moving"
```

The robot changes behaviour depending on:
- Position error
- Angular error

---

# Path Planning Logic

```python
self.final_x += math.cos(self.current_theta)*self.side_length
self.final_y += math.sin(self.current_theta)*self.side_length
self.final_theta += self.angle
```

This calculates:
- Next target coordinate
- Next target orientation

This is the logic that creates polygon movement.

---

# Speed Control Logic

Linear and angular speed are increased gradually:

```python
self.bot_linear_speed += self.accel
```

And reduced before reaching target:

```python
self.bot_linear_speed -= (self.deccel*self.Kp)
```

This creates smoother robot motion.

---

# 9. Installing ROS2

This project is tested on:
- Ubuntu 22.04
- ROS2 Humble

---

# Install ROS2 Humble

Follow official guide:

https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html

---

# Source ROS2

After installation:

```bash
source /opt/ros/humble/setup.bash
```

To avoid repeating every time:

```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

# Install turtlesim

```bash
sudo apt install ros-humble-turtlesim
```

Test installation:

```bash
ros2 run turtlesim turtlesim_node
```

---

# Install colcon

```bash
sudo apt install python3-colcon-common-extensions
```

---

# 10. Creating a ROS2 Workspace

Create workspace:

```bash
mkdir -p ~/ros2_ws/src
```

Go inside workspace:

```bash
cd ~/ros2_ws
```

Build workspace:

```bash
colcon build
```

Source workspace:

```bash
source install/setup.bash
```

---

# 11. Creating the Package

Go to source folder:

```bash
cd ~/ros2_ws/src
```

Create Python package:

```bash
ros2 pkg create --build-type ament_python turtle_shape_project
```

After creation, the structure becomes:

```text
ros2_ws/
 └── src/
      └── turtle_shape_project/
```

---

# 12. Writing the Node

Go inside Python module folder:

```bash
cd ~/ros2_ws/src/turtle_shape_project/turtle_shape_project
```

Create node file:

```bash
touch turtle_shape.py
```

Paste the project code inside:
- `turtle_shape.py`

Make file executable:

```bash
chmod +x turtle_shape.py
```

---

# 13. Adding Dependencies

Open:

```bash
package.xml
```

Add these dependencies inside the file:

```xml
<depend>rclpy</depend>
<depend>geometry_msgs</depend>
<depend>turtlesim</depend>
```

These are required because the project uses:
- ROS2 Python API
- Twist messages
- Pose messages

---

# Example package.xml

```xml
<?xml version="1.0"?>
<package format="3">
  <name>turtle_shape_project</name>
  <version>0.0.0</version>
  <description>ROS2 Turtle Shape Drawer</description>

  <maintainer email="yourmail@gmail.com">yourname</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>geometry_msgs</depend>
  <depend>turtlesim</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

---

# 14. Updating setup.py

Open:

```bash
setup.py
```

Inside `entry_points`, add:

```python
entry_points={
    'console_scripts': [
        'turtle_shape = turtle_shape_project.turtle_shape:main',
    ],
},
```

This tells ROS2:
- Which Python file to execute
- Which function is the entry point

---

# Example setup.py

```python
from setuptools import setup

package_name = 'turtle_shape_project'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yourname',
    maintainer_email='yourmail@gmail.com',
    description='ROS2 Turtle Shape Drawer',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'turtle_shape = turtle_shape_project.turtle_shape:main',
        ],
    },
)
```

---

# 15. Building the Workspace

Go to workspace root:

```bash
cd ~/ros2_ws
```

Build:

```bash
colcon build
```

Source workspace:

```bash
source install/setup.bash
```

---

# 16. Running the Project

# Terminal 1

Start turtlesim:

```bash
ros2 run turtlesim turtlesim_node
```

---

# Terminal 2

Source workspace:

```bash
source ~/ros2_ws/install/setup.bash
```

Run node:

```bash
ros2 run turtle_shape_project turtle_shape
```

---

# 17. Expected Output

The turtle should:
- Move forward
- Rotate
- Draw a polygon continuously

Current configuration:

```python
self.side_no = 6
```

So it draws a hexagon.

You can change:

```python
self.side_no
```

To create:
- Triangle
- Square
- Pentagon
- Octagon

etc.

---

# 18. Important ROS2 Commands

## List Topics

```bash
ros2 topic list
```

---

## View Topic Data

```bash
ros2 topic echo /turtle1/pose
```

---

## View Topic Information

```bash
ros2 topic info /turtle1/cmd_vel
```

---

## List Nodes

```bash
ros2 node list
```

---

## View Node Information

```bash
ros2 node info /turtle_shape
```

---

## View Interfaces Graphically

Install:

```bash
sudo apt install ros-humble-rqt-graph
```

Run:

```bash
rqt_graph
```

This visually shows:
- Publishers
- Subscribers
- Topic connections

---

## View Message Structure

```bash
ros2 interface show geometry_msgs/msg/Twist
```

---

## Monitor Topic Frequency

```bash
ros2 topic hz /turtle1/cmd_vel
```

---

# 19. How This Relates to Real Differential Drive AMRs

This project demonstrates the same architecture used in real robots.

Real AMRs use:
- Motor drivers
- Encoders
- IMU sensors
- Odometry
- PID controllers

Instead of:
```python
cmd.linear.x
```

Real robots convert velocity into:
- Left wheel RPM
- Right wheel RPM

The ROS2 node architecture remains almost identical.

---

# Differential Drive Equation

The robot motion is based on differential wheel speeds.

If:

```text
Left Wheel Speed = Right Wheel Speed
```

Robot moves straight.

If:

```text
Left Wheel Speed ≠ Right Wheel Speed
```

Robot turns.

---

# 20. Future Improvements

Possible improvements:

---

## PID Controller

Current controller is simple proportional logic.

Add:
- P control
- PI control
- PID control

For smoother motion.

---

## Simultaneous Turning and Moving

Currently:
- Move
- Stop
- Turn

Real robots often:
- Move and turn together

Using:
- Differential wheel velocities

---

## Odometry

Add odometry calculations.

---

## SLAM Integration

Use:
- LiDAR
- Mapping
- Localization

---

## Obstacle Avoidance

Add:
- Sensors
- Path replanning

---

## RViz Visualization

Visualize robot trajectory in RViz.

---

## Gazebo Simulation

Move from turtlesim to Gazebo for realistic physics.

---

## Hardware Integration

Run on:
- Raspberry Pi
- ESP32
- Jetson Nano

With:
- Motor drivers
- Encoders
- Sensors

---

## Dynamic Parameter Tuning

Add ROS2 parameters for:
- Speed
- Acceleration
- Polygon sides
- Thresholds

Without changing source code.

---

# 21. Conclusion

This project demonstrates the core robotics concepts used in real autonomous mobile robots:

- ROS2 communication
- Publishers and subscribers
- Closed-loop control
- State machines
- Velocity control
- Path planning
- Differential drive logic

Although implemented in `turtlesim`, the architecture directly reflects how real robots are controlled in robotics systems.

This project is an excellent beginner foundation for:
- ROS2 development
- Mobile robotics
- Autonomous systems
- Differential drive robot control
- Real-world AMR software architecture
