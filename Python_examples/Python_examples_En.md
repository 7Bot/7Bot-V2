# 7Bot Robotic Arm Python Examples Summary

**Version**: 2.1  
**Author**: Jerry Peng  
**Date**: July 2025  
**Update**: Support for both Serial and WebSocket dual protocol communication

## 📋 Overview

This folder contains complete Python programming examples for the 7Bot robotic arm, covering all aspects from basic control to advanced functionality. All examples support both Serial (USB) and WebSocket (WiFi) communication protocols, allowing users to choose the appropriate connection method based on their actual needs.

## 🚀 Example List

### 1. Basic Control Examples

#### [Exp1_angleCtrl.py](./Exp1_angleCtrl.py) - Joint Angle Control
- **Function Description**: Demonstrates how to control individual joint angles and set overall posture
- **Main Features**: 
  - Single joint angle control
  - Multi-joint posture setting
  - Support for Serial and WebSocket communication
- **Application Scenarios**: Learning basic joint control, understanding robotic arm motion principles

#### [Exp2_speedCtrl.py](./Exp2_speedCtrl.py) - Motion Speed Control
- **Function Description**: Shows how to set and control the motion speed of the robotic arm
- **Main Features**:
  - Low speed motion control
  - High speed motion control
  - Combined speed and posture control
- **Application Scenarios**: Applications requiring precise motion speed control

#### [Exp3_timeCtrl.py](./Exp3_timeCtrl.py) - Motion Time Control
- **Function Description**: Demonstrates how to control robotic arm motion through time parameters
- **Main Features**:
  - Time-based motion control
  - Precise time parameter settings
- **Application Scenarios**: Automated tasks requiring precise time control

### 2. Status Monitoring Examples

#### [Exp4_statusCtrl.py](./Exp4_statusCtrl.py) - System Status Control
- **Function Description**: Shows how to monitor and control the system status of the robotic arm
- **Main Features**:
  - System status monitoring
  - Status switching control
  - Real-time status feedback
- **Application Scenarios**: System debugging and status management

#### [Exp5_readAngle.py](./Exp5_readAngle.py) - Angle Reading
- **Function Description**: Demonstrates how to read real-time angles of each joint of the robotic arm
- **Main Features**:
  - Single joint angle reading
  - Multi-joint angle reading
  - Real-time angle monitoring
- **Application Scenarios**: Position feedback, angle monitoring, debugging analysis

#### [Exp6_setAngleAutoFb.py](./Exp6_setAngleAutoFb.py) - Angle Setting with Feedback
- **Function Description**: Shows how to set angles and obtain automatic feedback
- **Main Features**:
  - Angle setting and feedback
  - Automatic position confirmation
  - Closed-loop control demonstration
- **Application Scenarios**: Scenarios requiring precise position control

### 3. Advanced Function Examples

#### [Exp7_vacuumCtrl.py](./Exp7_vacuumCtrl.py) - Vacuum Gripper Control
- **Function Description**: Demonstrates how to control the vacuum gripper of the end effector
- **Main Features**:
  - Vacuum gripper on/off control
  - Gripper status management
  - End effector control
- **Application Scenarios**: Grasping, handling, assembly and other applications requiring end tool control

#### [Exp8_IKctrl.py](./Exp8_IKctrl.py) - Inverse Kinematics Control
- **Function Description**: Shows how to use inverse kinematics for Cartesian space control
- **Main Features**:
  - 5DOF inverse kinematics control
  - 6DOF inverse kinematics control
  - Cartesian coordinate control
  - Vector direction control
- **Application Scenarios**: Precise position control, path planning, complex motion tasks

### 4. System Management Examples

#### [Exp9_Info.py](./Exp9_Info.py) - System Information Retrieval
- **Function Description**: Demonstrates how to retrieve system information of the robotic arm
- **Main Features**:
  - Device code retrieval
  - Version information reading
  - MAC address retrieval
  - System configuration information
- **Application Scenarios**: System diagnosis, version management, device identification

#### [Exp10_SetID.py](./Exp10_SetID.py) - Device ID Setting
- **Function Description**: Shows how to set and modify the device ID of the robotic arm
- **Main Features**:
  - Device ID reading
  - Device ID setting
  - ID conflict detection
- **Application Scenarios**: Multi-device management, device configuration, network setup

## 🔧 Technical Features

### Communication Protocol Support
- **Serial Communication**: Through USB connection, stable and reliable
- **WebSocket Communication**: Through WiFi connection, supporting remote control
- **Protocol Switching**: Dynamic switching of communication protocols at runtime

### Programming Features
- **Asynchronous Support**: WebSocket mode supports asynchronous operations
- **Error Handling**: Comprehensive exception handling and retry mechanisms
- **Debug Mode**: Built-in debug output functionality
- **Cross-platform**: Support for Windows, macOS, Linux

### Dependencies
- **pyserial**: Serial communication support
- **websockets**: WebSocket client support
- **asyncio**: Asynchronous programming support (Python built-in)

## 📖 Usage Instructions

### Environment Preparation
1. Install Python 3.7+
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure 7Bot robotic arm is connected and powered

### Communication Configuration
- **Serial Mode**: Modify `SERIAL_PORT` to the corresponding port
- **WebSocket Mode**: Modify `ROBOT_IP` to the robotic arm's IP address

### Running Examples
```bash
# Run angle control example
python Exp1_angleCtrl.py

# Run inverse kinematics example
python Exp8_IKctrl.py
```

## 🔗 Related Documentation

- [Python API Technical Documentation](./README_PythonAPI.md) - Detailed API usage instructions
- [Dependency List](./requirements.txt) - Required Python packages
- [7Bot Robotic Arm User Manual](../Docs/7Bot桌面机械臂使用说明书.pdf)

## 💡 Development Recommendations

1. **Start from Basics**: It's recommended to run Exp1-Exp3 first to familiarize with basic control
2. **Understand Principles**: Each example contains detailed comments, it's recommended to read carefully
3. **Parameter Adjustment**: Adjust angles, speeds and other parameters according to the actual robotic arm
4. **Error Handling**: Pay attention to error messages and understand exception handling mechanisms
5. **Protocol Selection**: Choose appropriate communication protocols based on actual needs

## 🆘 Common Issues

### Connection Issues
- **Serial Connection Failure**: Check if the port number is correct and device is connected
- **WebSocket Connection Failure**: Check IP address and network connection

### Control Issues
- **Motion Abnormalities**: Check if angle ranges are within robotic arm limits
- **Speed Too Fast**: Reduce speed parameters to ensure safe motion

### Debugging Recommendations
- Enable `DEBUG_MODE = True` to view detailed communication information
- Use serial mode for initial testing to ensure basic functionality works
- Gradually switch to WebSocket mode for advanced functionality testing

---

**Note**: Please ensure the robotic arm is in a safe state before running examples to avoid collisions and accidental injuries.
