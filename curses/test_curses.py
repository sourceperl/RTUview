#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import time
import argparse
import socket
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

SERVER_HOST = "localhost"
SERVER_PORT = 502

# set global
regs       = []
clone_regs = []
poll_cycle = 0

# init a thread lock
regs_lock = Lock()

# parse args

def _ports(port):
    """
    Validates argparse port argument.
    """
    valid_range = range(1, 65535 + 1)
    try:
        port = int(port)
        if port not in valid_range:
            raise argparse.ArgumentTypeError("Port must be 1-65535")
        return port
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid range: " + port)

def _unit_id(u_id):
    """
    Validates argparse unit-id argument.
    """
    valid_range = range(0, 255 + 1)
    try:
        u_id = int(u_id)
        if u_id not in valid_range:
            raise argparse.ArgumentTypeError("Unit-id must be 0-255")
        return u_id
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid range: " + u_id)

def _hostname(name):
    """
    Validates argparse hostname argument.
    Accepts an ip address or a domain name.
    """
    try:
        socket.gethostbyname(name)
        return name
    except socket.gaierror:
        raise argparse.ArgumentTypeError("Invalid hostname: " + name)
    try:
        socket.inet_aton(name)
        return name
    except socket.error:
        raise argparse.ArgumentTypeError("Invalid ip address: " + name)

parser = argparse.ArgumentParser(description="Modbus RTU test utility.")
parser.add_argument("-H", "--host", default="localhost",
                    type=_hostname, help="hostname or IP address")
parser.add_argument("-P", "--port", default=502,
                    type=_ports, help="a TCP port")
parser.add_argument("-U", "--unit-id", default=1,
                    type=_unit_id, help="modbus unit-id")
args = parser.parse_args()

# modbus polling thread
def polling_thread():
    global regs, poll_cycle
    c = ModbusClient(host=args.host, port=args.port)
    # polling loop
    while True:
        # keep TCP open
        if not c.is_open():
            c.open()
        # do modbus reading on socket
        reg_list = c.read_holding_registers(0,10)
        # if read is ok, store result in regs (with thread lock synchronization)
        with regs_lock:
            if reg_list:
                regs = list(reg_list)
                poll_cycle += 1
            else:
                poll_cycle = 0
        # 1s before next polling
        time.sleep(0.2)

# start polling thread
tp = Thread(target=polling_thread)
# set daemon: polling thread will exit if main thread exit
tp.daemon = True
tp.start()

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)
    stdscr.nodelay(1)
    return stdscr

def close_curses(stdscr):
    stdscr.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

if __name__ == '__main__':
    try:
        stdscr = init_curses()
        init_colors()

        while True:
            stdscr.erase()
            stdscr.addstr(0, 1, "RTU Modbus real time", curses.A_BOLD)
            stdscr.addstr(1, 1, "Host = %s, Port = %s, Unit ID = %s" 
                                % (args.host, args.port, args.unit_id),
                          curses.A_BOLD)
            # non block get char (nodelay is set)
            c = stdscr.getch()
            # check "fix" request
            if (c == ord('f')) or (c == ord('F')):
                stdscr.addstr(2, 1, "FIX IS SET", curses.color_pair(1))
                clone_regs = []
            # print banner
            stdscr.addstr(5, 4, "----------------------------------------", curses.A_BOLD)
            stdscr.addstr(6, 4, "NTS   0 0 0 0  0 0 0 0  0 1 1 1  1 1 1 1", curses.A_BOLD)
            stdscr.addstr(7, 4, "      1 2 3 4  5 6 7 8  9 0 1 2  3 4 5 6", curses.A_BOLD)
            stdscr.addstr(8, 4, "----------------------------------------", curses.A_BOLD)
            # display data
            with regs_lock:
                if not poll_cycle:
                    stdscr.addstr(3, 4,
                                  "link KO",
                                  curses.color_pair(1))
                else:
                    stdscr.addstr(3, 4,
                                  "polling cycles: %s" % (str(poll_cycle)),
                                  curses.A_BOLD)
                # ensure clone is set
                if regs and not clone_regs:
                    clone_regs = list(regs)
                # display regs value
                # current line
                c_line = 9
                for i, value in enumerate(regs):
                    # current cursor and line
                    c_line  += 1
                    c_cursor = 4
                    # line name (ME or Txx)
                    stdscr.addstr(c_line, c_cursor,
                                  "ME    " if not i else "T%02d   " % i,
                                  curses.A_BOLD)
                    c_cursor += 6
                    # builts bits list for regs and clone
                    bits = utils.get_bits_from_int(value, val_size=16)
                    bits.reverse()
                    clone_bits = utils.get_bits_from_int(clone_regs[i],
                                                         val_size=16)
                    clone_bits.reverse()
                    # bit value (1 or " ")
                    for x, bit in enumerate(bits):
                        if clone_bits[x] == bits[x]:
                            stdscr.addstr(c_line, c_cursor,
                                          "1" if bit else ".",
                                          curses.A_NORMAL)
                        else:
                            stdscr.addstr(c_line, c_cursor,
                                          "1" if bit else ".",
                                          curses.A_REVERSE)
                        c_cursor += 2
                        # every 4 chars set a whitespace
                        if not (x+1)%4:
                            c_cursor += 1
            # refresh display, wait next
            stdscr.refresh()
            time.sleep(0.2)

    finally:
        close_curses(stdscr)
