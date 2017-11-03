#!/usr/bin/env python

def update_status_line(stdscr,height,c,query,ix):
    """
    render c (last char entered), query string so far, and horizontal char next
    into a status line display
    """
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
    "nuke completion area of display"
    iy = height-1
    while iy > 3:
        iy -= 1
        stdscr.move(iy,1)
        stdscr.clrtoeol()
        
def show_completions(stdscr,utorids,height,query,ix):
    "render the completions of query"
    if len(query) == 0:
        return
    iy = 3    #sorry.. top line is status, then ___, so start at line  3
    for o in utorids.keys():
        if o.startswith(query):
            if iy > height-1:
                break
            stdscr.move(iy,1)
            stdscr.clrtoeol()
            stdscr.addstr(o)
            stdscr.move(iy,10)
            stdscr.addstr(utorids[o])
            iy += 1
    stdscr.move(height-1,1)
    stdscr.addstr("_________________________________")
    stdscr.move(height,ix)

def refresh_view(stdscr,utorids,height,prompt,c,query,ix):
    "redraw status and completion areas"
    update_status_line(stdscr,height,c,query,ix)
    erase_completions(stdscr,height)
    show_completions(stdscr,utorids,height,query,ix)
    stdscr.move(height,1)
    stdscr.clrtoeol()
    stdscr.addstr(prompt)
    stdscr.addstr(query)
    
def longest_common_prefix(utorids,query):
    """
    return a tuple.. (flagTrueIfWholeCompletion,aStringPrefix) the flag tells if the prefix is the whole completion, the string is the prefix
    """
    if len(query) == 0:
        return (False,None)

    l = []
    for o in utorids.keys():
        if o.startswith(query):
            l.append(o)

    # forget it none of them start with query.
    if len(l) == 0:
        return (False,None)

    # an arbitrary utorid which startswith query
    an_opt = l[0] 

    # search for the longest prefix that all of l share.
    # can't be longer than length of an_opt, so only search that far

    prefix = query
    prev_prefix = ''
    verbose = False
    for ix in range(len(query),len(an_opt)+1):
        prev_prefix = prefix
        prefix = an_opt[:ix] #save longest so far..
        assert(len(prefix)==ix)
        if verbose: print("\r\nix",ix,"prefix", prefix)
        for o in l:
            if not o.startswith(prefix):
                if verbose: print("\r\nnope, prefix too long",prefix, prev_prefix)
                assert(prev_prefix)
                return (False,prev_prefix)

    #here if entire an_opt is longest common prefix
    if verbose: print("\r\nhere an_opt,prefix,prev_prefix",an_opt,prefix, prev_prefix)
    return (True,prefix)

def prompt_for_input_string_with_completions_curses(prompt,height,utorids):
    """
    beware: first (as in novice) attempt at curses programming.
    Prompt for a character, and show completions matching the query so far.
    Tab extends query so far with longest common completion.
    """
    import curses
    import curses.ascii

    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(True) #doesn't seem to help
    curses.noecho()

    # TODO: users terminal setting stty(1) actually determine what special keys do what
    # eg: I like ^C for interrupt and DEL for backspace,
    # some old-school users might have DEL as interrupt key.

    try:
        ix = 1
        query = ''
        c = ord(' ')
        refresh_view(stdscr,utorids,height,prompt,c,query,ix)

        # TODO: what to do if user hits return when query is not unique? Currently just return it.
        # thinking about beeping and then insisting on control-enter (or something) to really return.

        is_nasty_lf_hack = False
        
        while True:
            c = stdscr.getch()
            if True:
                update_status_line(stdscr,height,c,query,ix) #debug originally, but kinda looks okay

            if is_nasty_lf_hack:
                stdscr.move(height+1,2) ##hack
                stdscr.clrtoeol()
                
            if c == curses.ascii.LF:

                # we have it. query is exactly one of the utorids..
                if query in utorids.keys() or is_nasty_lf_hack:
                    is_nasty_lf_hack = False
                    break

                # if we have a query which uniquely identifies one utorid we return it.
                (is_whole,completion) = longest_common_prefix(utorids,query)

                # completion is the longest prefix of the all the utorid's starting with query --
                # but it might not be an entire utorid.
                # I'm thinking if the prefix is not an entire completion we should beep and demur.
                if is_whole:
                    query = completion
                    break

                # check if query uniquely identifies someone?
                n=0
                for id in utorids:
                    if id.startswith(query):
                        n += 1
                        
                if n != 1: 
                    refresh_view(stdscr,utorids,height,prompt,c,query,ix)
                    stdscr.move(height+1,2) ##hack
                    stdscr.addstr("query " +
                                  "`"  + query +
                                  "' is not an entire utorid.. enter again to return it")
                    is_nasty_lf_hack = True
                    
                # query not whole utorid, no good.. beep 
                curses.beep()
                refresh_view(stdscr,utorids,height,prompt,c,query,ix)
                continue
                    
            
            elif  c == curses.ascii.EOT: #end of file, control-d
                break
            
            elif c == curses.ascii.TAB: 
                is_nasty_lf_hack = False
                # TAB key set query to longest prefix amongst completions
                (flg,completion) = longest_common_prefix(utorids,query)
                if completion:
                    query = completion
                    c = ord(' ')
                    ix = len(query)+1
                else:
                    curses.beep()
                refresh_view(stdscr,utorids,height,prompt,c,query,ix)

            # TODO: learn how to make sure stty options are in effect for editing?
            elif c == curses.ascii.BS or c == curses.ascii.DEL: # backspace on my keyboard??
                is_nasty_lf_hack = False
                # delete last char from query, erase on screen
                query = query[:-1]
                if ix == 1:
                    curses.beep()
                else:
                    ix -= 1
                refresh_view(stdscr,utorids,height,prompt,c,query,ix)

            # this is getting on thin ice. stty determines which character "kills" all input
            elif c == curses.ascii.NAK: # aka ^U
                is_nasty_lf_hack = False
                assert(curses.ascii.isctrl(c))
                curses.beep()
                # blow away query, erase everything
                query = ''
                ix = 1
                refresh_view(stdscr,utorids,height,prompt,c,query,ix)
            
            else:
                is_nasty_lf_hack = False
                # append c to query and display c
                stdscr.addch(c)
                query += chr(c)
                ix += 1
                refresh_view(stdscr,utorids,height,prompt,c,query,ix)
        
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        if c == 4:
            return None
        else:
            return query

    except:
        curses.endwin()
        print("threw..")
        import traceback,sys
        traceback.print_exc(file=sys.stdout)
        return None



if __name__ == "__main__" :
    utorids = {
    "autorid1": "desc1",
    "autorid2longer": "desc1",
    "butorid1": "desc1",
    "butorid2": "desc1",
    "ab_utorid1": "desc1",
    "c_opt1": "desc1",
    "c_opt11": "desc1",
    "c_xxxxx": "desc1",
    }

    resp = prompt_for_input_string_with_completions_curses(">",10,utorids)
    print(resp)
