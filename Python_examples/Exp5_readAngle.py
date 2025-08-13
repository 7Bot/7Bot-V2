#!/usr/bin/python3 

# 7Bot Robotic Arm Example 5: Read Robot Pose (Enhanced with WebSocket Support)

# Date:    July 20th, 2020 (Updated: Dec 2025)
# Author:  Jerry Peng
 
import time 
from lib.Arm7Bot import Arm7Bot


# Communication Protocol Configuration
# =================================
# Choose your preferred communication method:
# 1. Serial Communication (USB Connection)
# 2. WebSocket Communication (WiFi Connection)

# Protocol selection: 'serial' or 'websocket'
PROTOCOL = 'serial'  # Change to 'websocket' for WiFi communication

# Serial Communication Settings
SERIAL_PORT = 'COM11'  # Change according to your system:
                      # "/dev/cu.SLAB_USBtoUART" on Mac OS
                      # "/dev/ttyUSB0" on Linux
                      # 'COM1' or 'COM11' on Windows

# WebSocket Communication Settings
ROBOT_IP = '192.168.4.1'      # Default robot IP address
WEBSOCKET_PORT = 8080         # Default WebSocket port
DEBUG_MODE = False            # Enable debug output

# Initialize robot connection based on protocol
if PROTOCOL == 'serial':
    print(f"Connecting to robot via Serial port: {SERIAL_PORT}")
    arm = Arm7Bot(port=SERIAL_PORT, protocol='serial', debug=DEBUG_MODE)
elif PROTOCOL == 'websocket':
    print(f"Connecting to robot via WebSocket: {ROBOT_IP}:{WEBSOCKET_PORT}")
    arm = Arm7Bot(ip=ROBOT_IP, websocket_port=WEBSOCKET_PORT, protocol='websocket', debug=DEBUG_MODE)
else:
    raise ValueError("Invalid protocol. Choose 'serial' or 'websocket'")

print(f"Successfully connected using {PROTOCOL.upper()} protocol")
print("Starting angle reading demonstration...")

# set arm to forceless status
print("Setting arm to forceless mode for manual manipulation...")
arm.setStatus(2)
arm.setAnglesFbFreq(0)  # Turn off feedback frequency

print("Reading joint angles (Press Ctrl+C to stop)...")
while(True):
    try:
        # 1. read individual joint's angle
        # angle_0 = arm.getAngle(0)
        # angle_1 = arm.getAngle(1)
        # print("angle of joint 0 is:", angle_0, "  angle of joint 1 is:", angle_1)

        # 2. read all joints' angle at once
        angles = arm.getAngles()
        print("Joints' Angles:", angles)

        time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nAngle reading demonstration stopped by user")
        break
    except Exception as e:
        print(f"Error reading angles: {e}")
        time.sleep(0.5)


