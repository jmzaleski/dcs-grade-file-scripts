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
    "aoption2longer",
    "boption1",
    "boption2",
    "ab_option1",
    "c_opt1",
    "c_opt11",
    "c_xxxxx",
    ]

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

def only_one_completion():
    if len(query) == 0:
        return None
    got_one = False
    one_completion = ''
    for o in options:
        if o.startswith(query):
            if got_one:
                return None #multiples match..
            else:
                got_one =  True
                one_completion = o
    return one_completion

def longest_completion():
    if len(query) == 0:
        return None
    longest_len = 0
    longest_completion = None
    for o in options:
        if o.startswith(query):
            l = len(o)
            if l > longest_len:
                longest_len = l
                longest_completion = o
    
    return longest_completion

import difflib
import os
def longest_common_prefix():

    if len(query) == 0:
        return None

    #collect the options that start with it.
    l = []
    for o in options:
        if o.startswith(query):
            l.append(o)

    assert(len(l) > 0)

    # if len(l) == 1:
    #     return l[0]

    an_opt = l[0] # an arbitrary element of the list of matches
    # search for the longest prefix that all of all l share.
    # can't be longer than length of an_opt, so only search that far
    #
    prefix = query
    prev_prefix = ''
    verbose = True
    verbose = False
    for ix in range(len(query),len(an_opt)+1):
        prev_prefix = prefix
        prefix = an_opt[:ix] #save longest so far..
        if verbose: print("\r\nix",ix,"prefix", prefix)
        # if all in l match prefix, can try longer prefix
        for o in l:
            if o.startswith(prefix):
                if verbose: print("\r\no startswith prefix ",o,prefix)
            else:
                assert(prev_prefix)
                if verbose: print("\r\nnope, prefix too long",prefix, prev_prefix)
                return prev_prefix

    #here if entire an_opt is longest common prefix
    if verbose: print("\r\nhere an_opt,prefix,prev_prefix",an_opt,prefix, prev_prefix)
    return prefix

try:
    ix = 1
    while 1:
        c = stdscr.getch()
        if True:
            update_status_line()

        if c == ord("\n") or c == 4: #EOF
            break

        elif c == 9: # TAB key
            #completion = only_one_completion()
            #completion = longest_completion()
            completion = longest_common_prefix()
            if completion:
                query = completion
                c = ord(' ')
                update_status_line()
                erase_completions()
                show_completions()
                stdscr.move(height,1)
                stdscr.clrtoeol()
                stdscr.addstr(query)
                stdscr.clrtoeol()
                ix = len(query)+1
            else:
                curses.beep()
                stdscr.move(height,ix)
                stdscr.clrtoeol()
                
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
    print(query)

except:
    curses.endwin()
    print("threw..")
    import traceback,sys
    traceback.print_exc(file=sys.stdout)
    exit(2)


