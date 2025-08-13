#!/usr/bin/python3 

# Project: Python Library for 7Bot Robotic Arm  ( Version 2.1.2 ) 
# Author: Artyom Liu & Jerry Peng
# Date:   July 2025
# Enhanced: Serial and WebSocket communication capabilities

import serial 
import time
import json
import asyncio
import websockets
from threading import Thread, Event
import queue


BAUD_RATE = 115200      # baud rate of robot serial port
SERVO_NUM = 7           # servo motor number of robot

# Register ID 
# ROM
DEVICE_TYPE_ID = 0
VERSION_ID = 1
MAC_ID = 2
# EEPROM
EEPROM_LEN = 9
EEPROM_ID = 11
DEVICE_ID = 11
BAUDRATE_ID = 12
OFFSET_ID = 13
# RAM 
EEPROM_LOCK_ID = 28
MOTOR_STATUS_ID = 29
EFFECTOR_ID = 30
VACUUM_ID = 31
SPEED_ID = 32
TIME_ID = 39
ANGLE_ID = 46
END_LENGTH_ID = 53
IK_ID = 54
IK_DATA_LENGTH = 9
IK7_DATA_LENGTH = 12
IK5_ID = 68
IK5_DATA_LENGTH = 6
ANGLE_FEEDBACK_FREQ_ID = 82
ANGLE_FEEDBACK_ID = 83
LOAD_FEEDBACK_FREQ_ID = 90
LOAD_FEEDBACK_ID = 91

# Constants for offset calculations
OFFSET_BIAS = 128
COORDINATE_OFFSET = 1024


class Arm7Bot: 
	"""The interface on host machine with 7Bot robot"""

	# Communication protocol options
	PROTOCOL_SERIAL = 'serial'
	PROTOCOL_WEBSOCKET = 'websocket'

	def __init__(self, port=None, ip='192.168.4.1', websocket_port=8080, protocol='serial', debug=False, timeout=5, max_retries=3): 
		"""
		Initialize 7Bot robot interface
		
		Parameters:
			port (str): Serial port name (for serial communication)
			ip (str): Robot IP address (for WebSocket communication)
			websocket_port (int): WebSocket service port
			protocol (str): Communication protocol ('serial' or 'websocket')
			debug (bool): Enable debug output
			timeout (float): Timeout in seconds
			max_retries (int): Maximum retry attempts
		"""
		self.protocol = protocol.lower()
		self.debug = debug
		self.timeout = timeout
		self.max_retries = max_retries
		
		# Serial communication setup
		if self.protocol == self.PROTOCOL_SERIAL:
			if port is None:
				raise ValueError("Serial port must be specified for serial communication")
			self.ser = serial.Serial(port, BAUD_RATE, timeout=0.2)
		
		# WebSocket communication setup
		elif self.protocol == self.PROTOCOL_WEBSOCKET:
			self.ip = ip
			self.websocket_port = websocket_port
			self.ws_url = f"ws://{self.ip}:{self.websocket_port}/ws"
			self.websocket = None
			self.ws_connected = False
			self.response_queue = queue.Queue()
			self.event_loop = None
			self.ws_thread = None
			self._connect_websocket()
		else:
			raise ValueError("Protocol must be 'serial' or 'websocket'")

	def _connect_websocket(self):
		"""Initialize WebSocket connection in a separate thread"""
		self.ws_connected = False
		self.stop_event = Event()
		
		# Start WebSocket thread
		self.ws_thread = Thread(target=self._websocket_thread, daemon=True)
		self.ws_thread.start()
		
		# Wait for connection
		for _ in range(50):  # Wait up to 5 seconds
			if self.ws_connected:
				break
			time.sleep(0.1)
		
		if not self.ws_connected:
			raise ConnectionError(f"Failed to connect to WebSocket server at {self.ws_url}")

	def _websocket_thread(self):
		"""WebSocket thread function"""
		self.event_loop = asyncio.new_event_loop()
		asyncio.set_event_loop(self.event_loop)
		
		try:
			self.event_loop.run_until_complete(self._websocket_client())
		except Exception as e:
			if self.debug:
				print(f"WebSocket thread error: {e}")
		finally:
			self.event_loop.close()

	async def _websocket_client(self):
		"""WebSocket client coroutine"""
		while not self.stop_event.is_set():
			try:
				if self.debug:
					print(f"Connecting to WebSocket: {self.ws_url}")
				
				async with websockets.connect(
					self.ws_url,
					timeout=self.timeout,
					ping_interval=30,
					ping_timeout=10
				) as websocket:
					self.websocket = websocket
					self.ws_connected = True
					
					if self.debug:
						print("WebSocket connected successfully")
					
					# Listen for messages
					while not self.stop_event.is_set():
						try:
							message = await asyncio.wait_for(
								websocket.recv(), 
								timeout=1.0
							)
							
							if self.debug:
								print(f"Received: {message}")
							
							# Put response in queue for synchronous access
							self.response_queue.put(message)
							
						except asyncio.TimeoutError:
							# Check if we should stop
							continue
						except websockets.exceptions.ConnectionClosed:
							if self.debug:
								print("WebSocket connection closed")
							break
							
			except Exception as e:
				if self.debug:
					print(f"WebSocket connection error: {e}")
				self.ws_connected = False
				
				if not self.stop_event.is_set():
					await asyncio.sleep(2)  # Wait before reconnecting

	def _send_websocket_command(self, data):
		"""Send command via WebSocket"""
		if not self.ws_connected or not self.websocket:
			raise ConnectionError("WebSocket not connected")
		
		json_data = json.dumps(data)
		if self.debug: 
			print(f"Sending WebSocket command: {json_data}")
		
		# Clear any old responses
		while not self.response_queue.empty():
			try:
				self.response_queue.get_nowait()
			except queue.Empty:
				break
		
		# Send command asynchronously
		future = asyncio.run_coroutine_threadsafe(
			self.websocket.send(json_data), 
			self.event_loop
		)
		
		try:
			future.result(timeout=self.timeout)
		except Exception as e:
			raise ConnectionError(f"Failed to send WebSocket command: {e}")
		
		# Wait for response if it's a read command
		if self._is_read_command(data):
			try:
				response = self.response_queue.get(timeout=self.timeout)
				if self.debug:
					print(f"WebSocket response: {response}")
				
				try:
					return json.loads(response)
				except json.JSONDecodeError:
					return {"status": response}
			except queue.Empty:
				return {"status": "WebSocket response timeout"}
		else:
			# For non-read commands, don't wait for response
			return {"status": "Command Sent"}

	def _is_read_command(self, data):
		"""Check if this is a read command"""
		return data.get("cmd") == "read"

	def switch_protocol(self, protocol, port=None, ip=None):
		"""
		Switch communication protocol
		
		Parameters:
			protocol (str): 'serial' or 'websocket'
			port (str): Serial port (required when switching to serial)
			ip (str): IP address (optional, updates current IP)
		"""
		if protocol.lower() not in [self.PROTOCOL_SERIAL, self.PROTOCOL_WEBSOCKET]:
			raise ValueError("Protocol must be 'serial' or 'websocket'")
			
		# Close current connections
		if self.protocol == self.PROTOCOL_SERIAL and hasattr(self, 'ser') and self.ser:
			self.ser.close()
		elif self.protocol == self.PROTOCOL_WEBSOCKET:
			self._disconnect_websocket()
			
		# Setup new protocol
		self.protocol = protocol.lower()
		
		if self.protocol == self.PROTOCOL_SERIAL:
			if port is None:
				raise ValueError("Serial port must be specified when switching to serial")
			self.ser = serial.Serial(port, BAUD_RATE, timeout=0.2)
			
		elif self.protocol == self.PROTOCOL_WEBSOCKET:
			if ip is not None:
				self.ip = ip
				self.ws_url = f"ws://{self.ip}:{self.websocket_port}/ws"
			self._connect_websocket()
				
		if self.debug:
			print(f"Switched to {self.protocol.upper()} protocol")

	def _disconnect_websocket(self):
		"""Disconnect WebSocket"""
		if hasattr(self, 'stop_event'):
			self.stop_event.set()
		
		if hasattr(self, 'ws_thread') and self.ws_thread:
			self.ws_thread.join(timeout=2)
		
		self.ws_connected = False
		self.websocket = None

	def ping(self):
		"""Send ping command to check WebSocket connection"""
		if self.protocol == self.PROTOCOL_WEBSOCKET:
			data = {"cmd": "ping"}
			return self._send_websocket_command(data)
		else:
			# For serial protocol, just return success
			return {"status": "ok", "message": "Serial protocol - ping not needed"}

	def readReg(self, addr, num): 
		"""Read register information"""
		if self.protocol == self.PROTOCOL_SERIAL:
			return self._readReg_serial(addr, num)
		else:
			return self._readReg_websocket(addr, num)
	
	def _readReg_serial(self, addr, num):
		"""Read register via serial communication"""
		# 先关闭掉角度自动反馈，避免冲突
		# self.setAnglesFbFreq(0)
		
		buf = [0x03, addr & 0xff, num & 0xff]
		self.writeSerial(buf) 
		
		ret_pack = self.readSerial()
		if ret_pack.pop(0) != 0x03:  
			raise serial.SerialException("mismatching pack type") 
		return ret_pack[2:]
	
	def _readReg_websocket(self, addr, num):
		"""Read register via WebSocket"""
		data = {"cmd": "read", "id": addr, "num": num}
		response = self._send_websocket_command(data)
		
		try:
			if isinstance(response, dict):
				if "data" in response:
					return [int(x) for x in response["data"]]
				elif "status" in response:
					if isinstance(response["status"], list):
						return response["status"]
					elif isinstance(response["status"], str) and "," in response["status"]:
						return [int(x) for x in response["status"].split(",")]
					else:
						try:
							return [int(response["status"])]
						except (ValueError, TypeError):
							if self.debug: print(f"Non-numeric register response: {response['status']}")
							return []
			
			if isinstance(response, str) and "," in response:
				return [int(x) for x in response.split(",")]
				
			return []
		except (ValueError, AttributeError, TypeError) as e:
			if self.debug: print(f"Error parsing register values: {e}, Response: {response}")
			return []
		
	def writeReg(self, addr: int, data: list):
		"""Write data to register"""
		if self.protocol == self.PROTOCOL_SERIAL:
			return self._writeReg_serial(addr, data)
		else:
			return self._writeReg_websocket(addr, data)
	
	def _writeReg_serial(self, addr: int, data: list):
		"""Write register via serial communication"""
		buf = [0x04, addr & 0xff, len(data) & 0xff]
		buf.extend(d & 0xff for d in data)
		self.writeSerial(buf)
		# information feedback from robot is not required so far 
	
	def _writeReg_websocket(self, addr: int, data: list):
		"""Write register via WebSocket"""
		if not isinstance(data, list):
			data = [data]
		cmd_data = {"cmd": "write", "id": addr, "num": len(data), "value": data}
		return self._send_websocket_command(cmd_data)
	
	def readAnglesFb(self, max_retries=3, retry_delay=0.1): 
		"""Read angles feedback with retry mechanism"""
		if self.protocol != self.PROTOCOL_SERIAL:
			# For WebSocket protocol, use readReg instead
			return self.readReg(ANGLE_FEEDBACK_ID, SERVO_NUM)
			
		# Serial implementation
		for attempt in range(max_retries):
			try:
				ret_pack = self.readSerial()
				if ret_pack.pop(0) != 0x05:  
					raise serial.SerialException("mismatching pack type") 
				if ret_pack.pop(0) != ANGLE_FEEDBACK_ID:
					raise serial.SerialException("mismatching pack type") 
				return ret_pack[1:]
			except serial.SerialTimeoutException:
				if attempt < max_retries - 1:
					print(f"Serial timeout, retrying... (attempt {attempt + 2}/{max_retries})")
					time.sleep(retry_delay)
				else:
					print("Serial communication failed after all retries")
					raise
			except serial.SerialException as e:
				print(f"Serial exception: {e}")
				if attempt < max_retries - 1:
					time.sleep(retry_delay)
				else:
					raise

	# Get Functions #

	def getDeviceCode(self):
		"""Get device code"""
		return self.readReg(DEVICE_TYPE_ID, 1)[0]

	def getVersion(self):
		"""Get version"""
		return self.readReg(VERSION_ID, 1)[0] / 10
	
	def getMAC(self):
		"""Get MAC address (length: 6 bytes)"""
		return self.listToString(self.readReg(MAC_ID, 6))

	def listToString(self, l: list):  
		"""Convert list of integers to MAC address format (XX:XX:XX:XX:XX:XX)"""
		return ':'.join([format(int(i), '02X') for i in l])

	def getID(self):
		"""Get device ID"""
		return self.readReg(DEVICE_ID, 1)[0]

	def getOffsets(self):
		"""Get joint offsets"""
		return self.readReg(OFFSET_ID, SERVO_NUM)

	def getAngle(self, ID: int):
		"""Get single joint angle
		ID: joint ID (range [0, 6])
		"""
		return self.readReg(ANGLE_FEEDBACK_ID + ID, 1)[0]

	def getAngles(self):
		"""Get all joint angles"""
		return self.readReg(ANGLE_FEEDBACK_ID, SERVO_NUM)

	def getLoad(self, ID: int):
		"""Get single joint load
		ID: joint ID (range [0, 6])
		"""
		return self.readReg(LOAD_FEEDBACK_ID + ID, 1)[0]

	def getLoads(self):
		"""Get all joint loads"""
		return self.readReg(LOAD_FEEDBACK_ID, SERVO_NUM)

	def getSystemInfo(self):
		"""Get system information"""
		try:
			info = {
				"device_code": self.getDeviceCode(),
				"version": self.getVersion(),
				"mac": self.getMAC(),
				"device_id": self.getID(),
				"protocol": self.protocol.upper()
			}
			return info
		except Exception as e:
			if self.debug:
				print(f"Error getting system info: {e}")
			return {}

	def getAllStatus(self):
		"""Get all robot status information"""
		try:
			status = {
				"system_info": self.getSystemInfo(),
				"angles": self.getAngles(),
				"loads": self.getLoads(),
				"motor_status": self.getMotorStatus(),
				"vacuum_status": self.getVacuumStatus()
			}
			return status
		except Exception as e:
			if self.debug:
				print(f"Error getting all status: {e}")
			return {}

	# Set Functions #

	def setID(self, ID: int):
		"""Set device ID"""
		return self.writeReg(DEVICE_ID, [ID])

	def setOffsets(self, offsets: list):
		"""Set joint offsets
		offsets: list of 7 offset values
		"""
		if len(offsets) != SERVO_NUM:
			raise ValueError(f"Offsets list must have {SERVO_NUM} elements")
		return self.writeReg(OFFSET_ID, offsets)

	def clearOffsets(self):
		"""Clear all joint offsets (set to zero)"""
		zero_offsets = [0] * SERVO_NUM
		return self.setOffsets(zero_offsets)

	def setLock(self, lock: int):
		"""Set EEPROM lock status: 0-unlock, 1-lock"""
		return self.writeReg(EEPROM_LOCK_ID, [lock])

	def setStatus(self, status: int):
		"""Set motor status
		Status: 0-protection mode (lock), 1-servo mode (unlock), 2-forceless mode
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			return self.writeReg(MOTOR_STATUS_ID, [status])
		else:
			# WebSocket protocol - use dedicated status command
			data = {"cmd": "status", "status": status}
			return self._send_websocket_command(data)

	def getMotorStatus(self):
		"""Get motor status: 0-protection, 1-servo, 2-forceless"""
		return self.readReg(MOTOR_STATUS_ID, 1)[0]

	def getVacuumStatus(self):
		"""Get vacuum status: 0-off, 1-on"""
		return self.readReg(VACUUM_ID, 1)[0]

	def setEffector(self, effector_type: int):
		"""Set effector type
		effector_type: type of end effector
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			return self.writeReg(EFFECTOR_ID, [effector_type])
		else:
			# WebSocket protocol - 使用寄存器写入方式
			return self.writeReg(EFFECTOR_ID, [effector_type])

	def setVacuum(self, vacuum: int):
		"""Set vacuum status: 0-turn off, 1-turn on"""
		if self.protocol == self.PROTOCOL_SERIAL:
			self.writeReg(VACUUM_ID, [vacuum])
		else:
			# WebSocket protocol
			data = {"cmd": "vacuum", "status": vacuum}
			return self._send_websocket_command(data)

	def setSpeed(self, speed: int):
		"""Set motion speed
		Speed: angular speed of joints motion (unit: 1.9°/s, range: [0, 100])
		if Speed = 0; it means set joints motion speed to the maximum, i.e. 190°/s
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			speeds = [speed] * SERVO_NUM
			self.writeReg(SPEED_ID, speeds)
		else:
			# WebSocket protocol
			data = {"cmd": "speed", "speed": speed}
			return self._send_websocket_command(data)

	def setTime(self, time: int):
		"""Set motion execute time
		Time: motion execute time (unit: 100ms, range: [0, 100])
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			times = [time] * SERVO_NUM
			self.writeReg(TIME_ID, times)
		else:
			# WebSocket protocol - 使用寄存器写入方式
			times = [time] * SERVO_NUM
			return self.writeReg(TIME_ID, times)

	def setAngle(self, ID: int, angle: int):
		"""Set individual joint
		ID: joint ID (range [0, 6])
		angle: joint angle (unit: degree, range: [0, 180])
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			self.writeReg(ANGLE_ID + ID, [angle])
		else:
			# WebSocket protocol
			data = {"cmd": "angle", "id": ID, "angle": angle}
			return self._send_websocket_command(data)

	def setAngles(self, angles: list):
		"""Set 7 joints angle (Unit: degree) at once, range: [0, 180]"""
		if self.protocol == self.PROTOCOL_SERIAL:
			self.writeReg(ANGLE_ID, angles)
		else:
			# WebSocket protocol
			data = {"cmd": "angles", "angles": angles}
			return self._send_websocket_command(data)

	def setIK6(self, j6: list, vec56: list):
		"""Set robot position use IK parameters. Function: IK6
		input joint[6] & Vector56(joint[5] to joint[6] direction), calculate theta[0]~[4]
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			data_ik = []
			for coord in j6:
				coord_offset = coord + COORDINATE_OFFSET
				data_ik.extend([coord_offset >> 8, coord_offset % 256])
			data_ik.extend(vec + OFFSET_BIAS for vec in vec56)
			self.writeReg(IK_ID, data_ik)
		else:
			# WebSocket protocol
			data = {"cmd": "IK6", "pos": j6, "vec56": vec56}
			return self._send_websocket_command(data)

	def setIK5(self, position: list):
		"""Set robot position use IK5 parameters. Function: IK5
		input joint[5] position (x, y, z), calculate theta[0]~[2]
		
		Parameters:
			position (list): 3D position [x, y, z] in mm
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			data_ik = []
			for coord in position:
				coord_offset = coord + COORDINATE_OFFSET
				data_ik.extend([coord_offset >> 8, coord_offset % 256])
			self.writeReg(IK5_ID, data_ik)
		else:
			# WebSocket protocol
			data = {"cmd": "IK5", "pos": position}
			return self._send_websocket_command(data)

	def setIK7(self, j6: list, vec56: list, vec67: list):
		"""Set robot position use IK parameters. Function: IK7
		input joint[6], Vector56(joint[5] to joint[6] direction) & Vector67(joint[6] to joint[7]), calculate theta[0]~[5]
		"""
		if self.protocol == self.PROTOCOL_SERIAL:
			data_ik = []
			for coord in j6:
				coord_offset = coord + COORDINATE_OFFSET
				data_ik.extend([coord_offset >> 8, coord_offset % 256])
			data_ik.extend(vec + OFFSET_BIAS for vec in vec56)
			data_ik.extend(vec + OFFSET_BIAS for vec in vec67)
			self.writeReg(IK_ID, data_ik)
		else:
			# WebSocket protocol  
			data = {"cmd": "IK7", "pos": j6, "vec56": vec56, "vec67": vec67}
			return self._send_websocket_command(data)

	def setAnglesFbFreq(self, freq: int):
		"""Set joints' angle auto feedback frequency
		Freq: frequency of joints' angle feedback (unit: Hz, range: [0~50])
		"""
		return self.writeReg(ANGLE_FEEDBACK_FREQ_ID, [freq])

	def setLoadsFbFreq(self, freq: int):
		"""Set joints' load auto feedback frequency
		Freq: frequency of joints' load feedback (unit: Hz, range: [0~50])
		"""
		return self.writeReg(LOAD_FEEDBACK_FREQ_ID, [freq])

	def reset(self):
		"""Reset robot to safe state"""
		try:
			# Set to protection mode first
			self.setStatus(0)
			time.sleep(0.5)
			
			# Set safe angles
			safe_angles = [90, 90, 90, 90, 90, 90, 90]
			self.setAngles(safe_angles)
			time.sleep(1)
			
			# Turn off vacuum
			self.setVacuum(0)
			
			if self.debug:
				print("Robot reset to safe state")
				
		except Exception as e:
			if self.debug:
				print(f"Error during reset: {e}")

	def home(self):
		"""Move robot to home position"""
		try:
			# Set to servo mode
			self.setStatus(1)
			time.sleep(0.5)
			
			# Move to home position - based on firmware initAngle values
			home_angles = [90, 90, 65, 90, 90, 90, 80]
			self.setAngles(home_angles)
			
			if self.debug:
				print("Robot moved to home position")
				
		except Exception as e:
			if self.debug:
				print(f"Error during home: {e}")

	def waitForMotion(self, timeout=10):
		"""Wait for motion to complete"""
		if self.protocol == self.PROTOCOL_SERIAL:
			# For serial, just wait a fixed time
			time.sleep(2)
			return
			
		# For WebSocket protocol, we can add a simple wait
		# In a real implementation, this could check motion status
		time.sleep(2)
		
		if self.debug:
			print("Motion wait completed")

	def EEPROMinit(self):
		"""EEPROM data init, this function will erase offset data"""
		data = [0, 0] + [OFFSET_BIAS] * 7
		self.setLock(0)
		self.writeReg(EEPROM_ID, data)
		self.setLock(1)

	def readSerial(self, max_header_attempts=50): 
		"""Read serial data with error checking (Serial protocol only)"""
		if self.protocol != self.PROTOCOL_SERIAL:
			raise RuntimeError("readSerial is only available in serial protocol mode")
			
		cnt = 0 
		# read pack head 
		while True: 
			tmp = self.ser.read() 
			if tmp == b'\xaa': 
				tmp = self.ser.read() 
				if tmp == b'\x77': 
					break 
			elif tmp == b'':  # No data received within timeout
				cnt += 1
				if cnt >= max_header_attempts:
					raise serial.SerialTimeoutException()
			cnt += 1 
			if cnt >= max_header_attempts * 2:  # Increased threshold for corrupted data
				raise serial.SerialTimeoutException() 
		
		# from here data is to be returned 
		tmp = self.ser.read(3) 
		ret = [0xaa, 0x77, tmp[0], tmp[1], tmp[2]]
		tmp = self.ser.read(ret[4] + 2) 
		ret.extend(tmp)
		crc = self.CRC16_MODBUS(ret[0:-2]) 
		if (crc & 0xff == ret[-2]) and ((crc >> 8) & 0xff == ret[-1]): 
			return ret[2:-2] 
		else: 
			raise serial.SerialException("data corrupted") 

	def writeSerial(self, data: list): 
		"""Write serial data with CRC (Serial protocol only)"""
		if self.protocol != self.PROTOCOL_SERIAL:
			raise RuntimeError("writeSerial is only available in serial protocol mode")
			
		buf = [0xaa, 0x77] 
		buf.extend(data)

		crc = self.CRC16_MODBUS(buf) 
		buf.extend([crc & 0xff, (crc >> 8) & 0xff])

		return self.ser.write(bytes(buf)) == len(buf) 

	def invert8(self, val): 
		"""Invert 8-bit value"""
		if val >= 0: 
			return val 
		else: 
			return 256 + val 

	def invert16(self, val): 
		"""Invert 16-bit value"""
		if val >= 0: 
			return val 
		else: 
			return 65536 + val

	def CRC16_MODBUS(self, data: list): 
		"""Calculate CRC16 MODBUS checksum"""
		crc = 0xFFFF 
		for pos in data: 
			crc ^= pos 
			for i in range(8): 
				if (crc & 1) != 0: 
					crc >>= 1 
					crc ^= 0xA001 
				else: 
					crc >>= 1 
		return crc 

	def __del__(self):
		"""Cleanup on destruction"""
		try:
			if self.protocol == self.PROTOCOL_SERIAL and hasattr(self, 'ser') and self.ser:
				self.ser.close()
			elif self.protocol == self.PROTOCOL_WEBSOCKET:
				self._disconnect_websocket()
		except:
			pass

