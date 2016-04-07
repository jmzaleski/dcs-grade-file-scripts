'''
Created on Apr 6, 2016

@author: mzaleski
'''

import matz_utils
import re

class LineHisto(object):
    '''
    classdocs
    '''


    def __init__(self, fn):
        '''
        Constructor
        '''
        self.msg = matz_utils.MessagePrinter(True)
        self.msg.setPrefix("GradeFileReader")
        self.cdfid_to_tut = {}
        try:
            self.grade_file = open(fn, 'rb')
        except:
            self.msg.error("failed to open", fn)
            
    def read(self):
        lines = []
        freq = {}
        for rawline in self.grade_file:
            line = rawline.rstrip() #how can we figure out what we took off?
            m = re.search("^Author:", line)
            if m:
                lines.append(line)
                if not line in freq:
                    freq[line] = 1
                else:
                    freq[line] += 1
        for k in freq.keys():
            print freq[k],k
        return lines        

import sys        
if __name__ == "__main__" :
    msg = matz_utils.MessagePrinter(True)
    if len(sys.argv) != 2 :
            msg.error("usage", sys.argv[0], "group-git.log")
    
    msg.verbose( sys.argv[1])
    fn = sys.argv[1]
    me = LineHisto(fn)
    rs = me.read()
