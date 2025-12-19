import minimalmodbus
import serial
import time

PORT = '/dev/ttyUSB0'
SLAVE_ID = 1

ins = minimalmodbus.Instrument(PORT, SLAVE_ID)
ins.serial.baudrate = 9600
ins.serial.bytesize = 8
ins.serial.parity   = serial.PARITY_NONE
ins.serial.stopbits = 1
ins.serial.timeout  = 1
ins.mode = minimalmodbus.MODE_RTU

print("Relay ON")
ins.write_register(0, 1, 0)   # Register 0 = ON
time.sleep(2)

print("Relay OFF")
ins.write_register(0, 0, 0)   # Register 0 = OFF

