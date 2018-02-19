#!/usr/bin/env python

class AppState:
    "store stuff"
    def __init__(self, initial_message):
        self.initial_message = initial_message

import curses.ascii
class AppViewer:
    "control the screen using curses"

    def __init__(self, height, appState):
        self.height = height
        self.appState = appState
        self.ungetc_buf_char = None
        import curses,curses.ascii
        self.stdscr = curses.initscr()
        curses.cbreak()
        self.stdscr.keypad(True) #doesn't seem to help
        curses.noecho()

    def cleanup(self):
        self.stdscr.keypad(False)
        import curses,curses.ascii #have to do this over and over??
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        
    def getch(self):
        if self.ungetc_buf_char:
            c = self.ungetc_buf_char
            self.ungetc_buf_char = None
            return c
        else:
            return self.stdscr.getch()

    def ungetch(self,c):
        "work around python curses ungetc not working"
        self.ungetc_buf_char = c
        
    def beep(self):
        import curses
        curses.beep()
        
    def show_warning_message(self,msg):
        "display msg below the input line"
        self.stdscr.move(self.height+1,1)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(msg)
        
    def update_status_line(self,c,query,ix):
        """
        render c (last char entered), query string so far, and horizontal char next
        into a status line display
        """
        self.stdscr.move(1,1)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(query)
        self.stdscr.move(1,20)
        self.stdscr.addch(c)
        self.stdscr.move(1,25)
        s = "%s" % int(c)
        self.stdscr.addstr(s)
        self.stdscr.move(2,1)
        self.stdscr.addstr("_________________________________")
        self.stdscr.move(self.height,ix)
      
    def erase_completions(self):
        "nuke completion area of display"
        iy = self.height-1
        while iy > 3:
            iy -= 1
            self.stdscr.move(iy,1)
            self.stdscr.clrtoeol()

    def get_stdscr(self):
        return self.stdscr
        
    def show_completions(self,utorid_to_name_number,query,ix):
        "render the completions of query"
        if len(query) == 0:
            return
        iy = 3    #sorry.. top line is status, then ___, so start at line  3
        for utorid in utorid_to_name_number.keys():
            if utorid.startswith(query):
                if iy > self.height-1:
                    break
                self.stdscr.move(iy,1)
                self.stdscr.clrtoeol()
                self.stdscr.addstr(utorid)
                self.stdscr.move(iy,10)
                self.stdscr.addstr(utorid_to_name_number[utorid])
                iy += 1
                self.stdscr.move(self.height-1,1)
                self.stdscr.addstr("_________________________________")
                self.stdscr.move(self.height,ix)

    def clear_warning_message(self):
        "clear warning line"
        self.stdscr.move(self.height+1,1)
        self.stdscr.clrtoeol()

    def refresh_view(self,utorids,prompt,c,query,ix):
        "redraw status and completion areas"
        self.update_status_line(c,query,ix)
        self.erase_completions()
        self.show_completions(utorids,query,ix)
        self.stdscr.move(self.height,1)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(prompt)
        self.stdscr.addstr(query)
        
    # TODO: learn how to make sure stty options are in effect for editing?

    def is_eof(self,c):
        return c == curses.ascii.EOT
    def is_lf(self,c):
        return c == curses.ascii.LF
    def is_tab(self,c):
        return c == curses.ascii.TAB
    def is_nak(self,c):
        # this is getting on thin ice. stty determines which character "kills" all input ^U for me..
        return c == curses.ascii.NAK
    def is_bs(self,c):
        return (c == curses.ascii.BS) or (c == curses.ascii.DEL) # backspace on my keyboard??
    
def longest_common_prefix(utorid_map,query):
    """
    return a tuple.. (flagTrueIfWholeCompletion,aStringPrefix) the flag tells if the prefix is the whole completion, the string is the prefix
    """
    if len(query) == 0:
        return (False,None)
    l = []

    for o in utorid_map.keys():
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

def prompt_for_input_string_with_completions_curses(prompt,height,utorid_map,initial_warning_message):
    """
    beware: first (as in novice) attempt at curses programming.
    Prompt for a character, and show completions matching the query so far.
    Tab extends query so far with longest common completion.
    """
    import curses.ascii

    av = AppViewer(height,initial_warning_message)
    #stdscr = av.get_stdscr()

    # TODO: users terminal setting stty(1) actually determine what special keys do what
    # eg: I like ^C for interrupt and DEL for backspace,
    # some old-school users might have DEL as interrupt key.

    try:
        ix = 1
        query = ''
        c = ord(' ')
        av.show_warning_message(initial_warning_message)
        av.refresh_view(utorid_map,prompt,c,query,ix)

        #input loop..
        while True:
            c1 = av.getch() 

            av.update_status_line(c,query,ix) #debug originally, but kinda looks okay
            av.clear_warning_message()
                
            if av.is_lf(c): #end of line ish
                if query in utorid_map.keys():
                    # done.. query is exactly one of the utorids..
                    break

                # if we have a query which uniquely identifies one utorid we return it.
                (is_whole,completion) = longest_common_prefix(utorid_map,query)

                # completion is the longest prefix of the all the utorid's starting with query --
                # but it might not be an entire utorid.
                if is_whole:
                    query = completion
                    break

                # might not be complete, but still may uniquely identifies someone?
                n=0
                for id in utorid_map:
                    if id.startswith(query):
                        n += 1
                        
                if n != 1: 
                    msg = "query " + "`"  + query + "' does not identify a unique utorid.. hit enter again to return it anyway: "
                    av.show_warning_message(msg)

                    av.beep()
                    c = av.getch()
                    if av.is_lf(c):
                        break
                    else:
                        # other than LF want to continue as normal.. ungetc..
                        av.ungetch(c)
                        av.clear_warning_message()
                        continue
            
            elif  av.is_eof(c): #end of file'ish
                break
            
            elif av.is_tab(c):
                # TAB key set query to longest prefix amongst completions
                (flg,completion) = longest_common_prefix(utorid_map,query)
                if completion:
                    query = completion
                    c = ord(' ')
                    ix = len(query)+1
                else:
                    curses.beep()
                av.refresh_view(utorid_map,prompt,c,query,ix)

            elif av.is_bs(c): #backspace
                # delete last char from query, erase on screen
                query = query[:-1]
                if ix == 1:
                    av.beep()
                else:
                    ix -= 1
                av.refresh_view(utorid_map,prompt,c,query,ix)

            elif av.is_nak(c): # control-u
                av.beep()
                # blow away query, erase everything
                query = ''
                ix = 1
                av.refresh_view(utorid_map,prompt,c,query,ix)
            
            else:
                # append c to query.
                query += chr(c)
                ix += 1
                av.refresh_view(utorid_map,prompt,c,query,ix)

        ############# end input loop..

        av.cleanup()
        if av.is_eof(c):
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
    utorid_map = {
    "autorid1": "desc1",
    "autorid2longer": "desc1",
    "butorid1": "desc1",
    "butorid2": "desc1",
    "ab_utorid1": "desc1",
    "c_opt1": "desc1",
    "c_opt11": "desc1",
    "c_xxxxx": "desc1",
    }

    resp = prompt_for_input_string_with_completions_curses(">",10,utorid_map,"initial warning message")
    print(resp)
