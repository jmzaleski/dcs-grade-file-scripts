#!/usr/bin/env python

import curses
import curses.textpad
import time

#curses.cbreak()
stdscr = curses.initscr()
#stdscr.keypad(True) #doesn't seem to work
curses.noecho()

#curses.echo()

begin_x = 20
begin_y = 7
height = 10
width = 40
win = curses.newwin(width,height, begin_y, begin_x)

stdscr.move(height,1)

options = [
    "aoption1",
    "aoption2",
    "boption1",
    "boption2",
    "ab_option1",
    ]
hw = "Hello world!"
query = ''

def update_status_line():
    stdscr.move(1,1)
    stdscr.clrtoeol()
    stdscr.addstr(query)
    stdscr.move(1,20)
    stdscr.addch(c)
    stdscr.move(1,25)
    s = "%s" % int(c)
    stdscr.addstr(s)
    stdscr.move(2,1)
    stdscr.addstr("_________________________________")
    stdscr.move(height,ix)


def erase_completions():
    iy = height
    while iy > 3:
        iy -= 1
        stdscr.move(iy,1)
        stdscr.clrtoeol()
        
def show_completions():
    if len(query) == 0:
        return
    iy = height
    for o in options:
        if o.startswith(query):
            iy -=1
            if iy < 3:
                break
            stdscr.move(iy,1)
            stdscr.clrtoeol()
            stdscr.addstr(o)
    stdscr.move(height,ix)
    
try:
    ix = 1
    while 1:
        c = stdscr.getch()
        if True:
            update_status_line()

        if c == ord("\n") or c == 4: #EOF
            break

        elif c == 9: # TAB key
            #print options above..
            y = height
            for o in options:
                if o.startswith(query):
                    y -=1
                    if y < 1:
                        break
                    stdscr.move(y,1)
                    stdscr.addstr(o)
            stdscr.move(height,ix)

        elif c == 127: # DEL key, backspace on my keyboard??
            query = query[:-1]
            update_status_line()
            erase_completions()
            show_completions()
            if ix == 1:
                curses.beep()
            else:
                ix -= 1
            stdscr.move(height,ix)
            stdscr.clrtoeol()

        elif c == 21: # ^U blow away line
            query = ''
            update_status_line()
            erase_completions()
            show_completions()
            ix = 1
            stdscr.move(height,ix)
            stdscr.clrtoeol()
            curses.beep()
            
        else:
            stdscr.addch(c)
            query += chr(c)
            update_status_line()
            erase_completions()
            show_completions()
            ix += 1
            
        stdscr.move(height,ix) #move on to the next place..
        
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

except:
    curses.endwin()
    print("threw..")
    import traceback,sys
    traceback.print_exc(file=sys.stdout)
    exit(2)


