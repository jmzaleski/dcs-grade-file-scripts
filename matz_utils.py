'''
Created on Apr 1, 2016

@author: mzaleski
'''
from __future__ import print_function  #allows print as function
import sys

class MessagePrinter:
    '''
    i dunno. stuff.
    '''
    def __init__(self, dbg):
        '''
        Constructor
        '''
        self.debugMode = dbg
        self.verboseMode = False
        self.prefix = ''

    def setVerbose(self):
        self.verboseMode = True
        
    def setPrefix(self, prefix):
        self.prefix = prefix
    
    def warning(self, *objs):
        print("WARNING: ", self.prefix, *objs, file=sys.stderr)
    
    def error(self,*objs):
        print("ERROR: ", self.prefix, *objs, file=sys.stderr)
        exit(42)
    
    def debug(self, *objs):
        if self.debugMode:
            print("DEBUG: ", self.prefix, *objs, file=sys.stdout)
            
    def debug_message(self, *objs):
        self.debug(*objs)
    
    def verbose_message(self, *objs):
        self.verbose(objs)
        
    def verbose(self, *objs):
        if self.verboseMode:
            print("VERBOSE: ", self.prefix, *objs, file=sys.stdout)

if __name__ == "__main__" :
    me = MessagePrinter(True)
    me.debug("hello from debug")