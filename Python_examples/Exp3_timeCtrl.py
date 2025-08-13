#!/usr/bin/python3 

# 7Bot Robotic Arm Example 3: Robot Motion Time Control (Enhanced with WebSocket Support)

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
print("Starting time control demonstration...")

# Motion speed has priority to motion time. So set speed to maximum at first.
print("Setting speed to maximum (0)...")
arm.setSpeed(0)

# 1. set short motion time
print("Setting short motion time (5 * 100ms = 500ms)...")
arm.setTime(5) # 5*100ms = 500ms
pose1 = [50,  80,  50,  50,  50,  50, 40]
arm.setAngles(pose1)
time.sleep(0.5)

# 2. set long motion time
print("Setting long motion time (30 * 100ms = 3000ms)...")
arm.setTime(30) # 30*100ms = 3000ms
pose2 = [130,  100,  80,  130,  130,  130, 80]
arm.setAngles(pose2)
time.sleep(3)

print("Time control demonstration completed!")