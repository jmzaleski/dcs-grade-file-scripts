#!/usr/bin/env python

class AppState:
    "store stuff"
    def __init__(self, initial_message,utorid_map ):
        self.initial_message = initial_message
        self.query = ''
        self.ix = 1
        self.utorid_map  = utorid_map 
        #TODO: add utorid_map and methods like longest_prefix, etc
        
    def clear_query(self):
        "clear line"
        self.ix = 1
        self.query = ''

    def add_char_to_query(self,c):
        "user types a char which we add to query"
        self.query += chr(c)
        self.ix += 1

    def set_query(self,q):
        self.query = q
        self.ix = len(q)+1

    def query_in_completion_map(self):
        return self.query in utorid_map.keys()        

    def is_query_empty(self):
        return self.ix == 1
    
    def back_space(self):
        "bs = back space = remove char from RH end of query"
        self.query = self.query[:-1]
        self.ix = len(self.query)+1
    
    def longest_common_prefix(self):
        """
        return a tuple.. (isWholeCompletion,aStringPrefix) the flag tells if the prefix is the whole completion, the string is the prefix
        """
        if len(self.query) == 0:
            return (False,None)
        l = []

        for o in self.utorid_map.keys():
            if o.startswith(self.query):
                l.append(o)
        # forget it none of them start with query.
        if len(l) == 0:
            return (False,None)

        # an arbitrary utorid which startswith query
        an_opt = l[0] 

        # search for the longest prefix that all of l share.
        # can't be longer than length of an_opt, so only search that far

        prefix = self.query
        prev_prefix = ''
        verbose = False
        for ix in range(len(self.query),len(an_opt)+1):
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

    def query_is_unique(self):
        if self.query_in_completion_map():
            return True
        # completion is the longest prefix of the all the utorid's starting with query --
        (is_whole,completion) = self.longest_common_prefix()
        if is_whole:
             app_state.set_query(completion)
             return True
        # might not be complete, but still may uniquely identifies someone?
        n=0
        for id in self.utorid_map:
            if id.startswith(self.query):
                n += 1
        return n == 1

import curses.ascii
class AppViewer:
    "control the screen using curses"

    def __init__(self, height, app_state):
        self.height = height
        self.app_state = app_state
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
        
    def update_status_line(self,c):
        """
        render c (last char entered), query string so far, and horizontal char next
        into a status line display
        """
        query = self.app_state.query
        ix = self.app_state.ix
        self.stdscr.move(1,1)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(self.app_state.query)
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
        
    def show_completions(self,utorid_to_name_number):
        "render the completions of query"
        query = self.app_state.query
        ix = self.app_state.ix
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

    def refresh_view(self,prompt,c):
        "redraw status and completion areas"
        self.update_status_line(c)
        self.erase_completions()
        self.show_completions(self.app_state.utorid_map)
        self.stdscr.move(self.height,1)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(prompt)
        self.stdscr.addstr(self.app_state.query)
        
    # TODO: learn how to make sure stty options are in effect for editing?

    def is_eof(self,c):
        return c == curses.ascii.EOT
    def is_lf(self,c):
        return c == curses.ascii.LF
    def is_tab(self,c):
        return c == curses.ascii.TAB
    def is_kill_input(self,c):
        # this is getting on thin ice. stty determines which character "kills" all input ^U for me..
        return c == curses.ascii.NAK
    def is_bs(self,c):
        return (c == curses.ascii.BS) or (c == curses.ascii.DEL) # backspace on my keyboard??
    

def prompt_for_input_string_with_completions_curses(prompt,height,completion_map,initial_warning_message):
    """
    beware: first (as in novice) attempt at curses programming.
    Prompt for a character, and show completions matching the query so far.
    Tab extends query so far with longest common completion.
    """
    import curses.ascii

    app_state = AppState(initial_warning_message,completion_map)
    app_viewer = AppViewer(height,app_state)

    # TODO: users terminal setting stty(1) actually determine what special keys do what
    # eg: I like ^C for interrupt and DEL for backspace,
    # some old-school users might have DEL as interrupt key.

    try:
        app_state.clear_query()
        c = ord(' ')
        app_viewer.show_warning_message(initial_warning_message)
        app_viewer.refresh_view(prompt,c)

        while True:
            c = app_viewer.getch() 
            app_viewer.update_status_line(c)
            app_viewer.clear_warning_message()
                
            if app_viewer.is_lf(c): #### end of line ish
                if app_state.query_is_unique():
                    break;
                msg = "query " + "`"  + app_state.query + "' does not identify a unique utorid.. hit enter again to return it anyway: "
                app_viewer.show_warning_message(msg)
                app_viewer.beep()
                c = app_viewer.getch()
                if app_viewer.is_lf(c):
                    break
                else:
                    # other than LF want to continue as normal.. ungetc..
                    app_viewer.ungetch(c)
                    app_viewer.clear_warning_message()
            
            elif  app_viewer.is_eof(c): #end of file'ish
                break
            
            elif app_viewer.is_tab(c):
                (flg,completion) = app_state.longest_common_prefix()
                if completion:
                    app_state.set_query(completion)
                    c = ord(' ')
                else:
                    curses.beep()

            elif app_viewer.is_bs(c):
                if app_state.is_query_empty():
                    app_viewer.beep()
                else:
                    app_state.back_space()

            elif app_viewer.is_kill_input(c):
                app_viewer.beep()
                app_state.clear_query()
            else:
                app_state.add_char_to_query(c)
                
            app_viewer.refresh_view(prompt,c)

        ############# end input loop..

        app_viewer.cleanup()
        if app_viewer.is_eof(c): #ya think? (when i hit ^d i mean i'm finished with input.)
            return None
        else:
            return app_state.query

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
