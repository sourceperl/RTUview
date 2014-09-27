#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import time
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

SERVER_HOST = "localhost"
SERVER_PORT = 502

# set global
regs = []

# init a thread lock
regs_lock = Lock()

# modbus polling thread
def polling_thread():
    global regs
    c = ModbusClient(host=SERVER_HOST, port=SERVER_PORT)
    # polling loop
    while True:
        # keep TCP open
        if not c.is_open():
            c.open()
        # do modbus reading on socket
        reg_list = c.read_holding_registers(0,10)
        # if read is ok, store result in regs (with thread lock synchronization)
        if reg_list:
            with regs_lock:
                regs = reg_list
        # 1s before next polling
        time.sleep(0.4)

# start polling thread
tp = Thread(target=polling_thread)
# set daemon: polling thread will exit if main thread exit
tp.daemon = True
tp.start()

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
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

        x = 0

        while True:
            x += 1
            stdscr.erase()
            stdscr.addstr(1, 1, "i = %d" % (x), curses.color_pair(1))
            with regs_lock:
                for i, value in enumerate(regs):
                    stdscr.addstr(i+3, 3, "%d = %d" % (i, value),
                                  curses.color_pair(2))
            stdscr.refresh()
            time.sleep(0.5)

#            stdscr.erase()
#            stdscr.addstr(2, 1, "xxxxxxxx", curses.A_BOLD)
#            stdscr.refresh()
#            time.sleep(2)

        c = stdscr.getch()

    finally:
        close_curses(stdscr)
