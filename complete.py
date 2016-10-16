import readline
import logging

LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG,
                    )


class SimpleCompleter(object):
    """cribbed from python readline documentation"""

    def __init__(self, cl, predicate):
        self.completion_list = sorted(cl)
        self.matches = []
        self.predicate = predicate  # function to select completions
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so find the elements
            # of the completion list that match text
            if text:
                self.matches = [s
                                for s in self.completion_list
                                if s and self.predicate(text, s)]  # s.startswith(text)]
                logging.debug('%s matches: %s', repr(text), self.matches)
            else:
                self.matches = self.completion_list[:]
                logging.debug('(empty input) matches: %s', self.matches)

        # Return the state'th item from the match list,
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s', repr(text), state, repr(response))
        return response


def input_loop():
    line = ''
    while line != 'stop':
        #line = raw_input('Prompt ("stop" to quit): ')
        line = input('Prompt ("stop" to quit): ')  #pycharm
        print('Dispatch %s' % line)

if __name__ == "__main__":
    # Register our completer function
    cl_predicate = lambda entered_text, cl_candidate: cl_candidate.startswith(entered_text)
    readline.set_completer(SimpleCompleter(['start', 'stop', 'list', 'print'],cl_predicate).complete)

    # Use the tab key for completion
    # hack from stackoverflow. os/x python is a bit different because built atop BSD libedit
    #
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    # Prompt the user for text
    input_loop()
