from services.relay_rs485 import RelayRS485
import time

print("START TEST")

r = RelayRS485()

print("Relay 1 ON")
r.relay_on(1)
time.sleep(1)

print("Relay 1 OFF")
r.relay_off(1)

print("DONE")
