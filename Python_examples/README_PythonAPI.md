# 7Bot 机械臂 Python API 技术文档

**版本**: 2.1.2  
**作者**: Artyom Liu & Jerry Peng  
**日期**: July 2025  
**更新**: 支持串口和WebSocket双协议通信

## 📋 概述

7Bot Python API 是一个完整的机械臂控制库，支持串口和WebSocket两种通信协议。该API提供了直观的Python接口，可以轻松控制7Bot机械臂的所有功能，包括关节控制、逆运动学、状态监控等。

### 🚀 主要特性

- **双协议支持**: 串口通信 + WebSocket实时通信
- **完整功能覆盖**: 支持固件v2.1.2的所有功能
- **异步WebSocket**: 基于asyncio的高效WebSocket通信
- **错误处理**: 完善的异常处理和重试机制
- **调试支持**: 内置调试输出功能
- **线程安全**: WebSocket通信使用独立线程

## 🔧 安装和依赖

### 必需依赖

```bash
pip install pyserial websockets asyncio
```

### 依赖库说明

- **pyserial**: 串口通信支持
- **websockets**: WebSocket客户端支持
- **asyncio**: 异步编程支持（Python内置）
- **threading**: 线程管理（Python内置）
- **queue**: 线程间通信（Python内置）

## 🏗️ 架构设计

### 通信协议架构

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

### 类结构设计

```python
class Arm7Bot:
    # 协议常量
    PROTOCOL_SERIAL = 'serial'
    PROTOCOL_WEBSOCKET = 'websocket'
    
    # 核心方法
    def __init__()           # 初始化连接
    def switch_protocol()    # 协议切换
    def ping()              # 连接测试
    
    # 寄存器操作
    def readReg()           # 读取寄存器
    def writeReg()          # 写入寄存器
    
    # 获取功能
    def getDeviceCode()     # 获取设备代码
    def getVersion()        # 获取版本
    def getMAC()           # 获取MAC地址
    def getID()            # 获取设备ID
    def getOffsets()       # 获取偏差值
    def getAngle()         # 获取单关节角度
    def getAngles()        # 获取所有角度
    def getLoad()          # 获取单关节负载
    def getLoads()         # 获取所有负载
    def getSystemInfo()    # 获取系统信息
    def getAllStatus()     # 获取所有状态
    
    # 设置功能
    def setID()            # 设置设备ID
    def setOffsets()       # 设置偏差值
    def clearOffsets()     # 清除偏差值
    def setLock()          # 设置EEPROM锁定
    def setStatus()        # 设置电机状态
    def setEffector()      # 设置末端执行器
    def setVacuum()        # 设置真空吸盘
    def setSpeed()         # 设置运动速度
    def setTime()          # 设置运动时间
    def setAngle()         # 设置单关节角度
    def setAngles()        # 设置所有角度
    
    # 逆运动学
    def setIK5()           # 5DOF逆运动学
    def setIK6()           # 6DOF逆运动学
    def setIK7()           # 7DOF逆运动学
    
    # 高级功能
    def reset()            # 复位到安全状态
    def home()             # 移动到初始位置
    def waitForMotion()    # 等待运动完成
```

## 🔌 连接和初始化

### 串口连接

```python
from Arm7Bot import Arm7Bot

# 串口连接
robot = Arm7Bot(
    port='COM3',           # Windows串口
    # port='/dev/ttyUSB0', # Linux串口
    protocol='serial',
    debug=True
)
```

### WebSocket连接

```python
# WebSocket连接
robot = Arm7Bot(
    ip='192.168.4.1',      # 机器人IP地址
    websocket_port=8080,   # WebSocket端口
    protocol='websocket',
    debug=True,
    timeout=5
)
```

### 协议切换

```python
# 从串口切换到WebSocket
robot.switch_protocol('websocket', ip='192.168.1.100')

# 从WebSocket切换到串口
robot.switch_protocol('serial', port='COM3')
```

## 📡 通信协议详解

### 串口协议

#### 数据包格式
```
[0xAA][0x77][Type][Length][Data...][CRC_L][CRC_H]
```

#### 命令类型
- `0x03`: 读取寄存器
- `0x04`: 写入寄存器
- `0x05`: 角度反馈

#### CRC校验
使用CRC16 MODBUS算法确保数据完整性。

### WebSocket协议

#### 连接地址
```
ws://[IP]:8080/ws
```

#### 消息格式
```json
{
  "cmd": "命令名称",
  "参数名": "参数值"
}
```

#### 响应格式
```json
{
  "status": "ok|error",
  "message": "操作结果描述",
  "data": [数据数组]
}
```

## 🎛️ 核心功能API

### 设备信息获取

```python
# 获取设备代码
device_code = robot.getDeviceCode()
print(f"Device Code: {device_code}")

# 获取固件版本
version = robot.getVersion()
print(f"Firmware Version: {version}")

# 获取MAC地址
mac = robot.getMAC()
print(f"MAC Address: {mac}")

# 获取设备ID
device_id = robot.getID()
print(f"Device ID: {device_id}")

# 获取系统信息
info = robot.getSystemInfo()
print(f"System Info: {info}")
```

### 关节控制

```python
# 设置单个关节角度
robot.setAngle(0, 90)  # 关节0设置为90度

# 设置所有关节角度
angles = [90, 90, 90, 90, 90, 90, 90]
robot.setAngles(angles)

# 获取当前角度
current_angle = robot.getAngle(0)
all_angles = robot.getAngles()
print(f"Joint 0: {current_angle}°")
print(f"All joints: {all_angles}")
```

### 运动参数设置

```python
# 设置运动速度 (0-100)
robot.setSpeed(50)

# 设置运动时间 (0-100, 单位: 100ms)
robot.setTime(10)  # 1秒

# 设置电机状态
robot.setStatus(1)  # 0:保护模式, 1:伺服模式, 2:无力模式
```

### 逆运动学控制

```python
# 5DOF逆运动学 - 控制末端位置
position = [100, 200, 150]  # [x, y, z] mm
robot.setIK5(position)

# 6DOF逆运动学 - 控制位置和方向
position = [100, 200, 150]  # [x, y, z] mm
vec56 = [0, 0, 1]          # 关节5到6的方向向量
robot.setIK6(position, vec56)

# 7DOF逆运动学 - 完整控制
position = [100, 200, 150]  # [x, y, z] mm
vec56 = [0, 0, 1]          # 关节5到6的方向向量
vec67 = [0, 1, 0]          # 关节6到7的方向向量
robot.setIK7(position, vec56, vec67)
```

### 末端执行器控制

```python
# 真空吸盘控制
robot.setVacuum(1)  # 开启
robot.setVacuum(0)  # 关闭

# 获取真空状态
vacuum_status = robot.getVacuumStatus()
print(f"Vacuum: {'ON' if vacuum_status else 'OFF'}")

# 设置末端执行器类型
robot.setEffector(1)  # 设置执行器类型
```

### 偏差值管理

```python
# 获取当前偏差值
offsets = robot.getOffsets()
print(f"Current offsets: {offsets}")

# 设置偏差值
new_offsets = [1, -2, 0, 1, -1, 0, 1]
robot.setOffsets(new_offsets)

# 清除所有偏差值
robot.clearOffsets()
```

### 负载监控

```python
# 获取单个关节负载
load = robot.getLoad(0)
print(f"Joint 0 load: {load}")

# 获取所有关节负载
loads = robot.getLoads()
print(f"All loads: {loads}")
```

## 🔧 高级功能

### 连接测试

```python
# Ping测试连接
response = robot.ping()
print(f"Ping response: {response}")
```

### 安全操作

```python
# 复位到安全状态
robot.reset()

# 移动到初始位置
robot.home()

# 等待运动完成
robot.waitForMotion(timeout=10)
```

### 状态监控

```python
# 获取完整状态信息
status = robot.getAllStatus()
print(f"Complete status: {status}")

# 获取电机状态
motor_status = robot.getMotorStatus()
status_names = {0: "Protection", 1: "Servo", 2: "Forceless"}
print(f"Motor status: {status_names.get(motor_status, 'Unknown')}")
```

### 反馈频率设置

```python
# 设置角度反馈频率 (0-50Hz)
robot.setAnglesFbFreq(10)

# 设置负载反馈频率 (0-50Hz)
robot.setLoadsFbFreq(5)
```

## 📊 寄存器映射

### ROM寄存器 (只读)

| 地址 | 名称 | 说明 |
|------|------|------|
| 0 | DEVICE_TYPE_ID | 设备类型：7 |
| 1 | VERSION_ID | 固件版本：21 (2.1) |
| 2 | MAC_ID | MAC地址 (6字节) |

### EEPROM寄存器 (可读写)

| 地址 | 名称 | 说明 |
|------|------|------|
| 11 | DEVICE_ID | 设备ID |
| 12 | BAUDRATE_ID | 波特率设置 |
| 13 | OFFSET_ID | 系统偏差值 (7字节) |

### RAM寄存器 (可读写)

| 地址 | 名称 | 说明 |
|------|------|------|
| 28 | EEPROM_LOCK_ID | EEPROM锁定状态 |
| 29 | MOTOR_STATUS_ID | 电机状态：0-保护，1-伺服，2-无力 |
| 30 | EFFECTOR_ID | 末端执行器状态 |
| 31 | VACUUM_ID | 真空吸盘：0-关闭，1-打开 |
| 32-38 | SPEED_ID | 各关节速度设置 |
| 39-45 | TIME_ID | 各关节运动时间 |
| 46-52 | ANGLE_ID | 各关节目标角度 |
| 83-89 | ANGLE_FEEDBACK_ID | 各关节当前角度 (只读) |
| 91-97 | LOAD_FEEDBACK_ID | 各关节当前负载 (只读) |

## 🐛 错误处理和调试

### 异常类型

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

### 调试模式

```python
# 启用调试输出
robot = Arm7Bot(port='COM3', debug=True)

# 调试输出示例
# [DEBUG] Sending WebSocket command: {"cmd":"angle","id":1,"angle":90}
# [DEBUG] WebSocket response: {"status":"ok","message":"Angle set"}
```

### 连接状态检查

```python
# WebSocket连接状态
if robot.protocol == 'websocket':
    if robot.ws_connected:
        print("WebSocket connected")
    else:
        print("WebSocket disconnected")

# 串口连接状态
if robot.protocol == 'serial':
    if robot.ser.is_open:
        print("Serial port open")
    else:
        print("Serial port closed")
```

## 📝 使用示例

### 基础控制示例

```python
from Arm7Bot import Arm7Bot
import time

# 初始化连接
robot = Arm7Bot(ip='192.168.4.1', protocol='websocket', debug=True)

try:
    # 测试连接
    print("Testing connection...")
    robot.ping()
    
    # 获取系统信息
    info = robot.getSystemInfo()
    print(f"Robot info: {info}")
    
    # 设置到伺服模式
    robot.setStatus(1)
    time.sleep(0.5)
    
    # 移动到初始位置
    robot.home()
    time.sleep(2)
    
    # 执行简单动作序列
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
    
    # 复位到安全状态
    robot.reset()
    
except Exception as e:
    print(f"Error: {e}")
finally:
    # 清理连接
    del robot
```

### 逆运动学示例

```python
# 6DOF逆运动学控制
def move_to_position(x, y, z, direction=[0, 0, 1]):
    """移动到指定位置和方向"""
    try:
        robot.setIK6([x, y, z], direction)
        time.sleep(2)
        print(f"Moved to position [{x}, {y}, {z}]")
    except Exception as e:
        print(f"Failed to move: {e}")

# 使用示例
move_to_position(100, 200, 150)  # 移动到位置(100, 200, 150)
move_to_position(0, 200, 100, [1, 0, 0])  # 移动到位置并指定方向
```

### 状态监控示例

```python
def monitor_robot_status():
    """监控机器人状态"""
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

# 启动监控
monitor_robot_status()
```

## 🔄 版本历史

### v2.1.2 (当前版本)
- ✅ 支持固件v2.1.2的所有功能
- ✅ 完整的WebSocket协议支持
- ✅ 添加ping命令功能
- ✅ 添加clearOffsets功能
- ✅ 支持无力模式(状态2)
- ✅ 完善的错误处理
- ✅ 线程安全的WebSocket通信

### v2.1.0
- 基础串口和WebSocket支持
- 核心控制功能
- 逆运动学支持

## 📞 技术支持

### 常见问题

1. **连接失败**
   - 检查IP地址和端口
   - 确认机器人固件版本
   - 检查网络连接

2. **WebSocket连接超时**
   - 增加timeout参数
   - 检查防火墙设置
   - 确认WebSocket服务运行

3. **串口连接问题**
   - 检查串口名称
   - 确认波特率设置
   - 检查USB连接

### 调试技巧

1. 启用debug模式查看详细日志
2. 使用ping()测试连接状态
3. 检查getSystemInfo()获取设备信息
4. 监控getAllStatus()了解完整状态

---

**注意**: 使用前请确保机器人固件版本兼容，并按照安全操作规程进行操作。 