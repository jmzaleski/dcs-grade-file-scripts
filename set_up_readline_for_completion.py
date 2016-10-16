
def set_up_readline(cl):
    """UI: python hackery to configure readline do completion on an array"""

    # Tell readline to use tab key for completion
    # hack from stackoverflow. os/x python is a bit different because built atop BSD libedit
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    import logging
    LOG_FILENAME = '/tmp/completer.log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.ERROR, ) #logging.DEBUG for verbosity

    # completer will be used by readline library when it sees a tab.
    # Hard to find a decent writeup of the protocol.
    # Seems that when you hit tab on text it calls with state 0.
    # this is when you're supposed to find the matches for text in completion_list
    # Then, each time it calls with state 1,2, and we're supposed to return the corresponding completion
    if True:
        from complete import SimpleCompleter
        # our completer should offer user utorid's that start with the text user enters
        cl_predicate =  lambda entered_text, cl_candidate: cl_candidate.startswith(entered_text)
        readline.set_completer( SimpleCompleter(cl, cl_predicate).complete)
    else:
        # ******** doesn't work somebody tell me why **************
        # I'm obviously not understanding some subtle aspect of python closures.

        matches_for_closure = []

        # A completer instance will be used by readline library when it sees a tab.
        # clue?? pycharm complains:
        # This inspection detects names that should resolve but don't.
        # Due to dynamic dispatch and duck typing, this is possible in a limited but useful number of cases.
        # Top-level and class-level items are supported better than instance items.

        def hack(saved_matches, cl): # i wanna closure over saved_matches and cl!
            def complete(text, state):
                logging.debug("complete(text=%s, state=%s)", text, state)
                logging.debug("matches=%s)", saved_matches) #how come saved_matches unresolved?

                response = None
                if state == 0:
                    # This is the first time for this text, so build a match list.
                    logging.debug("state == 0")
                    if text:
                        saved_matches = [s for s in cl if s and s.startswith(text)]
                        logging.debug('%s matches: %s', repr(text), saved_matches)
                    else:
                        matches = cl[:]  # all possible completions
                        logging.debug('(empty input) matches: %s', saved_matches)

                # Return the state'th item from the match list,
                try:
                    response = saved_matches[state]
                except IndexError:
                    response = None
                logging.debug('complete(%s, %s) => %s', repr(text), state, repr(response))
                return response
            readline.set_completer(complete)
        hack(matches_for_closure, cl)
