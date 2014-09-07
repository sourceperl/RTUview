#!/usr/bin/python2.7
import sys
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

SERVER_HOST = "localhost"
SERVER_PORT = 502
EOL         = "\n"

c = ModbusClient(host=SERVER_HOST, port=SERVER_PORT)

if not c.open():
    print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

# banner
sys.stdout.write("----------------------------------------" + EOL)
sys.stdout.write("NTS   0 0 0 0  0 0 0 0  0 1 1 1  1 1 1 1" + EOL)
sys.stdout.write("      1 2 3 4  5 6 7 8  9 0 1 2  3 4 5 6" + EOL)
sys.stdout.write("----------------------------------------" + EOL)

# do modbus read
regs = c.read_holding_registers(20610, 20)
c.close()

# if read ok
if regs:
    for i, value in enumerate(regs):
        # builts bits list
        bits = utils.get_bits_from_int(value, val_size=16)
        bits.reverse()
        # line name (ME or Txx)
        sys.stdout.write("ME    " if not i else "T%02d   " % i)
        # bit value (1 or " ")
        for x, bit in enumerate(bits):
            sys.stdout.write("1 " if bit else ". ")
            if not (x+1)%4:
                sys.stdout.write(" ")
        sys.stdout.write(EOL)

