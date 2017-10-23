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
    len_longest_prefix = 0
    longest_comment_prefix = None
    for o in options:
        s = difflib.SequenceMatcher(None, o, query)
        match = s.find_longest_match(0, len(o), 0, len(query))
        l = match.size
        #print("match",match.a,match.b,match.size)
        if l > len_longest_prefix:
            len_longest_prefix = l
            longest_comment_prefix = o[:len_longest_prefix]

    #okay, so now have the the longest common thingy.. collect the options that start with it
    l = []
    prefix = longest_comment_prefix
    for o in options:
        if o.startswith(longest_comment_prefix):
            l.append(o)

    assert(len(l) > 0)
    if len(l) == 1:
        return l[0]
    
    prefix = longest_comment_prefix
    an_opt = l[0]
    for ix in range(len_longest_prefix,len(an_opt)+1):
        for o in l:
            if o.startswith(prefix):
                prefix = an_opt[:ix-1] #save longest so far..
            else:
                assert(prefix)
                return prefix
    #here if entire an_opt is longest common prefix
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


