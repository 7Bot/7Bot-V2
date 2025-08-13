#!/usr/bin/python3 

# 7Bot Robotic Arm Example 10: Set Robot ID (Enhanced with WebSocket Support)

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
print("Starting robot ID modification demonstration...")

# 先关闭掉自动反馈，避免数据冲突
print("Disabling automatic feedback to avoid data conflicts...")
arm.setAnglesFbFreq(0)
time.sleep(0.5)

try:
    # Get current ID
    print("Getting current robot ID...")
    id = arm.getID()
    print(f"Current ID: {id}")
    
    # Set new ID (increment by 1)
    new_id = id + 1
    print(f"Setting new ID to: {new_id}")
    
    # Unlock EEPROM for writing
    print("Unlocking EEPROM...")
    arm.setLock(0) # 关闭锁 
    
    # Set new ID
    arm.setID(new_id)
    
    # Lock EEPROM
    print("Locking EEPROM...")
    arm.setLock(1) # 打开锁
    
    time.sleep(0.5)
    
    # Verify new ID
    print("Verifying new ID...")
    id = arm.getID()
    print(f"New ID: {id}")
    
    if id == new_id:
        print("✓ ID successfully updated!")
    else:
        print("✗ ID update failed!")
        
except Exception as e:
    print(f"Error during ID modification: {e}")

print("Robot ID modification demonstration completed!")
