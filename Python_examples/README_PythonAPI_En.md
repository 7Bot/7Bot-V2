# 7Bot Robotic Arm Python API Technical Documentation

**Version**: 2.1.2  
**Author**: Artyom Liu & Jerry Peng  
**Date**: July 2025  
**Update**: Support for dual protocol communication via Serial and WebSocket

## 📋 Overview

7Bot Python API is a comprehensive robotic arm control library that supports both Serial and WebSocket communication protocols. This API provides an intuitive Python interface to easily control all functions of the 7Bot robotic arm, including joint control, inverse kinematics, status monitoring, and more.

### 🚀 Key Features

- **Dual Protocol Support**: Serial communication + WebSocket real-time communication
- **Complete Function Coverage**: Supports all features of firmware v2.1.2
- **Asynchronous WebSocket**: Efficient WebSocket communication based on asyncio
- **Error Handling**: Comprehensive exception handling and retry mechanisms
- **Debug Support**: Built-in debug output functionality
- **Thread Safety**: WebSocket communication uses independent threads

## 🔧 Installation and Dependencies

### Required Dependencies

```bash
pip install pyserial websockets asyncio
```

### Dependency Library Description

- **pyserial**: Serial port communication support
- **websockets**: WebSocket client support
- **asyncio**: Asynchronous programming support (Python built-in)
- **threading**: Thread management (Python built-in)
- **queue**: Inter-thread communication (Python built-in)

## 🏗️ Architecture Design

### Communication Protocol Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Python API    │    │   Serial Port   │    │   7Bot Robot    │
│                 │◄──►│                 │◄──►│                 │
│  Arm7Bot Class  │    │   USB/Serial    │    │   Firmware      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│   WebSocket     │◄─────────────┘
                        │   Server        │
                        │   (Port 8080)   │
                        └─────────────────┘
```

### Class Structure Design

```python
class Arm7Bot:
    # Protocol constants
    PROTOCOL_SERIAL = 'serial'
    PROTOCOL_WEBSOCKET = 'websocket'
    
    # Core methods
    def __init__()           # Initialize connection
    def switch_protocol()    # Protocol switching
    def ping()              # Connection testing
    
    # Register operations
    def readReg()           # Read register
    def writeReg()          # Write register
    
    # Get functions
    def getDeviceCode()     # Get device code
    def getVersion()        # Get version
    def getMAC()           # Get MAC address
    def getID()            # Get device ID
    def getOffsets()       # Get offset values
    def getAngle()         # Get single joint angle
    def getAngles()        # Get all angles
    def getLoad()          # Get single joint load
    def getLoads()         # Get all loads
    def getSystemInfo()    # Get system information
    def getAllStatus()     # Get all status
    
    # Set functions
    def setID()            # Set device ID
    def setOffsets()       # Set offset values
    def clearOffsets()     # Clear offset values
    def setLock()          # Set EEPROM lock
    def setStatus()        # Set motor status
    def setEffector()      # Set end effector
    def setVacuum()        # Set vacuum suction
    def setSpeed()         # Set motion speed
    def setTime()          # Set motion time
    def setAngle()         # Set single joint angle
    def setAngles()        # Set all angles
    
    # Inverse kinematics
    def setIK5()           # 5DOF inverse kinematics
    def setIK6()           # 6DOF inverse kinematics
    def setIK7()           # 7DOF inverse kinematics
    
    # Advanced functions
    def reset()            # Reset to safe state
    def home()             # Move to initial position
    def waitForMotion()    # Wait for motion completion
```

## 🔌 Connection and Initialization

### Serial Connection

```python
from Arm7Bot import Arm7Bot

# Serial connection
robot = Arm7Bot(
    port='COM3',           # Windows serial port
    # port='/dev/ttyUSB0', # Linux serial port
    protocol='serial',
    debug=True
)
```

### WebSocket Connection

```python
# WebSocket connection
robot = Arm7Bot(
    ip='192.168.4.1',      # Robot IP address
    websocket_port=8080,   # WebSocket port
    protocol='websocket',
    debug=True,
    timeout=5
)
```

### Protocol Switching

```python
# Switch from serial to WebSocket
robot.switch_protocol('websocket', ip='192.168.1.100')

# Switch from WebSocket to serial
robot.switch_protocol('serial', port='COM3')
```

## 📡 Communication Protocol Details

### Serial Protocol

#### Data Packet Format
```
[0xAA][0x77][Type][Length][Data...][CRC_L][CRC_H]
```

#### Command Types
- `0x03`: Read register
- `0x04`: Write register
- `0x05`: Angle feedback

#### CRC Verification
Uses CRC16 MODBUS algorithm to ensure data integrity.

### WebSocket Protocol

#### Connection Address
```
ws://[IP]:8080/ws
```

#### Message Format
```json
{
  "cmd": "command_name",
  "parameter_name": "parameter_value"
}
```

#### Response Format
```json
{
  "status": "ok|error",
  "message": "Operation result description",
  "data": [data_array]
}
```

## 🎛️ Core Function API

### Device Information Retrieval

```python
# Get device code
device_code = robot.getDeviceCode()
print(f"Device Code: {device_code}")

# Get firmware version
version = robot.getVersion()
print(f"Firmware Version: {version}")

# Get MAC address
mac = robot.getMAC()
print(f"MAC Address: {mac}")

# Get device ID
device_id = robot.getID()
print(f"Device ID: {device_id}")

# Get system information
info = robot.getSystemInfo()
print(f"System Info: {info}")
```

### Joint Control

```python
# Set single joint angle
robot.setAngle(0, 90)  # Set joint 0 to 90 degrees

# Set all joint angles
angles = [90, 90, 90, 90, 90, 90, 90]
robot.setAngles(angles)

# Get current angles
current_angle = robot.getAngle(0)
all_angles = robot.getAngles()
print(f"Joint 0: {current_angle}°")
print(f"All joints: {all_angles}")
```

### Motion Parameter Settings

```python
# Set motion speed (0-100)
robot.setSpeed(50)

# Set motion time (0-100, unit: 100ms)
robot.setTime(10)  # 1 second

# Set motor status
robot.setStatus(1)  # 0: Protection mode, 1: Servo mode, 2: Forceless mode
```

### Inverse Kinematics Control

```python
# 5DOF inverse kinematics - Control end position
position = [100, 200, 150]  # [x, y, z] mm
robot.setIK5(position)

# 6DOF inverse kinematics - Control position and orientation
position = [100, 200, 150]  # [x, y, z] mm
vec56 = [0, 0, 1]          # Direction vector from joint 5 to 6
robot.setIK6(position, vec56)

# 7DOF inverse kinematics - Complete control
position = [100, 200, 150]  # [x, y, z] mm
vec56 = [0, 0, 1]          # Direction vector from joint 5 to 6
vec67 = [0, 1, 0]          # Direction vector from joint 6 to 7
robot.setIK7(position, vec56, vec67)
```

### End Effector Control

```python
# Vacuum suction control
robot.setVacuum(1)  # Turn on
robot.setVacuum(0)  # Turn off

# Get vacuum status
vacuum_status = robot.getVacuumStatus()
print(f"Vacuum: {'ON' if vacuum_status else 'OFF'}")

# Set end effector type
robot.setEffector(1)  # Set effector type
```

### Offset Value Management

```python
# Get current offset values
offsets = robot.getOffsets()
print(f"Current offsets: {offsets}")

# Set offset values
new_offsets = [1, -2, 0, 1, -1, 0, 1]
robot.setOffsets(new_offsets)

# Clear all offset values
robot.clearOffsets()
```

### Load Monitoring

```python
# Get single joint load
load = robot.getLoad(0)
print(f"Joint 0 load: {load}")

# Get all joint loads
loads = robot.getLoads()
print(f"All loads: {loads}")
```

## 🔧 Advanced Functions

### Connection Testing

```python
# Ping test connection
response = robot.ping()
print(f"Ping response: {response}")
```

### Safety Operations

```python
# Reset to safe state
robot.reset()

# Move to initial position
robot.home()

# Wait for motion completion
robot.waitForMotion(timeout=10)
```

### Status Monitoring

```python
# Get complete status information
status = robot.getAllStatus()
print(f"Complete status: {status}")

# Get motor status
motor_status = robot.getMotorStatus()
status_names = {0: "Protection", 1: "Servo", 2: "Forceless"}
print(f"Motor status: {status_names.get(motor_status, 'Unknown')}")
```

### Feedback Frequency Settings

```python
# Set angle feedback frequency (0-50Hz)
robot.setAnglesFbFreq(10)

# Set load feedback frequency (0-50Hz)
robot.setLoadsFbFreq(5)
```

## 📊 Register Mapping

### ROM Registers (Read-only)

| Address | Name | Description |
|---------|------|-------------|
| 0 | DEVICE_TYPE_ID | Device type: 7 |
| 1 | VERSION_ID | Firmware version: 21 (2.1) |
| 2 | MAC_ID | MAC address (6 bytes) |

### EEPROM Registers (Read/Write)

| Address | Name | Description |
|---------|------|-------------|
| 11 | DEVICE_ID | Device ID |
| 12 | BAUDRATE_ID | Baud rate settings |
| 13 | OFFSET_ID | System offset values (7 bytes) |

### RAM Registers (Read/Write)

| Address | Name | Description |
|---------|------|-------------|
| 28 | EEPROM_LOCK_ID | EEPROM lock status |
| 29 | MOTOR_STATUS_ID | Motor status: 0-Protection, 1-Servo, 2-Forceless |
| 30 | EFFECTOR_ID | End effector status |
| 31 | VACUUM_ID | Vacuum suction: 0-Off, 1-On |
| 32-38 | SPEED_ID | Individual joint speed settings |
| 39-45 | TIME_ID | Individual joint motion time |
| 46-52 | ANGLE_ID | Individual joint target angles |
| 83-89 | ANGLE_FEEDBACK_ID | Individual joint current angles (read-only) |
| 91-97 | LOAD_FEEDBACK_ID | Individual joint current loads (read-only) |

## 🐛 Error Handling and Debugging

### Exception Types

```python
try:
    robot.setAngles([90, 90, 90, 90, 90, 90, 90])
except ConnectionError as e:
    print(f"Connection error: {e}")
except ValueError as e:
    print(f"Value error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Debug Mode

```python
# Enable debug output
robot = Arm7Bot(port='COM3', debug=True)

# Debug output example
# [DEBUG] Sending WebSocket command: {"cmd":"angle","id":1,"angle":90}
# [DEBUG] WebSocket response: {"status":"ok","message":"Angle set"}
```

### Connection Status Check

```python
# WebSocket connection status
if robot.protocol == 'websocket':
    if robot.ws_connected:
        print("WebSocket connected")
    else:
        print("WebSocket disconnected")

# Serial connection status
if robot.protocol == 'serial':
    if robot.ser.is_open:
        print("Serial port open")
    else:
        print("Serial port closed")
```

## 📝 Usage Examples

### Basic Control Example

```python
from Arm7Bot import Arm7Bot
import time

# Initialize connection
robot = Arm7Bot(ip='192.168.4.1', protocol='websocket', debug=True)

try:
    # Test connection
    print("Testing connection...")
    robot.ping()
    
    # Get system information
    info = robot.getSystemInfo()
    print(f"Robot info: {info}")
    
    # Set to servo mode
    robot.setStatus(1)
    time.sleep(0.5)
    
    # Move to initial position
    robot.home()
    time.sleep(2)
    
    # Execute simple action sequence
    positions = [
        [90, 90, 90, 90, 90, 90, 90],
        [45, 90, 90, 90, 90, 90, 90],
        [135, 90, 90, 90, 90, 90, 90],
        [90, 90, 90, 90, 90, 90, 90]
    ]
    
    for pos in positions:
        robot.setAngles(pos)
        time.sleep(1)
        current_angles = robot.getAngles()
        print(f"Current angles: {current_angles}")
    
    # Reset to safe state
    robot.reset()
    
except Exception as e:
    print(f"Error: {e}")
finally:
    # Clean up connection
    del robot
```

### Inverse Kinematics Example

```python
# 6DOF inverse kinematics control
def move_to_position(x, y, z, direction=[0, 0, 1]):
    """Move to specified position and orientation"""
    try:
        robot.setIK6([x, y, z], direction)
        time.sleep(2)
        print(f"Moved to position [{x}, {y}, {z}]")
    except Exception as e:
        print(f"Failed to move: {e}")

# Usage example
move_to_position(100, 200, 150)  # Move to position (100, 200, 150)
move_to_position(0, 200, 100, [1, 0, 0])  # Move to position and specify direction
```

### Status Monitoring Example

```python
def monitor_robot_status():
    """Monitor robot status"""
    while True:
        try:
            status = robot.getAllStatus()
            print(f"Robot Status:")
            print(f"  Angles: {status['angles']}")
            print(f"  Loads: {status['loads']}")
            print(f"  Motor Status: {status['motor_status']}")
            print(f"  Vacuum: {status['vacuum_status']}")
            print("-" * 40)
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Monitoring error: {e}")
            break

# Start monitoring
monitor_robot_status()
```

## 🔄 Version History

### v2.1.2 (Current Version)
- ✅ Support for all features of firmware v2.1.2
- ✅ Complete WebSocket protocol support
- ✅ Added ping command functionality
- ✅ Added clearOffsets functionality
- ✅ Support for forceless mode (status 2)
- ✅ Comprehensive error handling
- ✅ Thread-safe WebSocket communication

### v2.1.0
- Basic serial and WebSocket support
- Core control functions
- Inverse kinematics support

## 📞 Technical Support

### Common Issues

1. **Connection Failure**
   - Check IP address and port
   - Confirm robot firmware version
   - Check network connection

2. **WebSocket Connection Timeout**
   - Increase timeout parameter
   - Check firewall settings
   - Confirm WebSocket service is running

3. **Serial Connection Issues**
   - Check serial port name
   - Confirm baud rate settings
   - Check USB connection

### Debugging Tips

1. Enable debug mode to view detailed logs
2. Use ping() to test connection status
3. Check getSystemInfo() to get device information
4. Monitor getAllStatus() to understand complete status

---

**Note**: Before use, please ensure the robot firmware version is compatible and follow safe operation procedures.
