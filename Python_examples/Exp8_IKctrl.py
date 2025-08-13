#!/usr/bin/python3 

# 7Bot Robotic Arm Example 8: Robot IK(Inverse Kinematics) Control (Enhanced with WebSocket Support)

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
DEBUG_MODE = True             # Enable debug output - CHANGED FROM False

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
print("Starting IK control demonstration...")

# Ensure robot is in servo mode before IK control
print("Setting robot to servo mode...")
arm.setStatus(1)  # Set to servo mode
time.sleep(1)

# Set appropriate speed
print("Setting motion speed...")
arm.setSpeed(30)  # Set moderate speed
time.sleep(0.5)

# IK6 control
print("Moving to position 1 using IK6: [-50, 185, 50] with vector [0, 0, -1]")
arm.setIK6([-50, 185, 50], [0, 0, -1])
time.sleep(3)  # Increased wait time

print("Moving to position 2 using IK6: [50, 185, 50] with vector [0, 0, -1]")
arm.setIK6([50, 185, 50], [0, 0, -1])
time.sleep(3)  # Increased wait time

# Testing out of range position
print("Testing out of range position [500, 185, 50] - this should trigger an alarm...")
try:
    arm.setIK6([500, 185, 50], [0, 0, -1])
    time.sleep(2)
except Exception as e:
    print(f"Expected error for out of range position: {e}")

print("IK control demonstration completed!")
