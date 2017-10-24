#!/usr/bin/env python

def update_status_line(stdscr,height,c,query,ix):
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


def erase_completions(stdscr,height):
    iy = height
    while iy > 3:
        iy -= 1
        stdscr.move(iy,1)
        stdscr.clrtoeol()
        
def show_completions(stdscr,height,query,ix):
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

def refresh_view(stdscr,height,c,query,ix):
    "redraw three panes"
    update_status_line(stdscr,height,c,query,ix)
    erase_completions(stdscr,height)
    show_completions(stdscr,height,query,ix)
    
def longest_common_prefix(query):
    if len(query) == 0:
        return None

    l = []
    for o in options:
        if o.startswith(query):
            l.append(o)
    if len(l) == 0:
        return None

    # an arbitrary element of the list of matches
    an_opt = l[0] 

    # search for the longest prefix that all of all l share.
    # can't be longer than length of an_opt, so only search that far
    #
    prefix = query
    prev_prefix = ''
    verbose = False
    for ix in range(len(query),len(an_opt)+1):
        prev_prefix = prefix
        prefix = an_opt[:ix] #save longest so far..
        if verbose: print("\r\nix",ix,"prefix", prefix)
        # if all in l match prefix, can try longer prefix
        for o in l:
            if not o.startswith(prefix):
                if verbose: print("\r\nnope, prefix too long",prefix, prev_prefix)
                assert(prev_prefix)
                return prev_prefix

    #here if entire an_opt is longest common prefix
    if verbose: print("\r\nhere an_opt,prefix,prev_prefix",an_opt,prefix, prev_prefix)
    return prefix

def curses_input_string_with_completions(options):
    """
    beware: first (as in novice) attempt at curses programming.
    Prompt for a character, and show completions matching the query so far.
    Tab extends query so far with longest common completion.
    """
    import curses

    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(True) #doesn't seem to help
    curses.noecho()

    height = 10

    try:
        ix = 1
        query = ''
        while True:
            c = stdscr.getch()
            if True:
                update_status_line(stdscr,height,c,query,ix) #debug originally, but kinda looks okay

            if c == ord("\n") or c == 4: #EOF
                break

            elif c == 9: # TAB key
                # tab key set query to longest prefix amongst completions
                print("hello")
                completion = longest_common_prefix(query)
                if completion:
                    query = completion
                    c = ord(' ')
                    refresh_view(stdscr,height,c,query,ix)
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
                # delete last char from query, erase on screen
                query = query[:-1]
                refresh_view(stdscr,height,c,query,ix)
                if ix == 1:
                    curses.beep()
                else:
                    ix -= 1
                    # erase line following ix
                    stdscr.move(height,ix)
                    stdscr.clrtoeol()

            elif c == 21: # ^U 
                # blow away query, erase everything
                query = ''
                refresh_view(stdscr,height,c,query,ix)
                ix = 1
                stdscr.move(height,ix)
                stdscr.clrtoeol()
                curses.beep()
            
            else:
                # append c to query and display c
                stdscr.addch(c)
                query += chr(c)
                refresh_view(stdscr,height,c,query,ix)
                ix += 1
                stdscr.move(height,ix) #move on to the next place..
        
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        return query

    except:
        curses.endwin()
        print("threw..")
        import traceback,sys
        traceback.print_exc(file=sys.stdout)
        return None



if __name__ == "__main__" :
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

    resp = curses_input_string_with_completions(options)
    print(resp)
