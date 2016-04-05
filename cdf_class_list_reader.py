'''
Created on Apr 1, 2016

@author: mzaleski
'''
from __future__ import print_function  #allows print as function
import matz_utils
import re

class CdfClassListFileReader:
    '''
    read cdf class list files
    '''

    def __init__(self, fn):
        '''
        Constructor
        '''
        self.msg = matz_utils.MessagePrinter(False)
        self.msg.setPrefix("CdfClassListFileReader")
        
        try:
            self.cdf_file = open(fn, 'rb')
        except:
            print("eh?",fn)
            self.msg.error("failed to open", fn)
        self.cdfid_to_name_map = {}
    
    def extractCdfid(self, line):
        (d,csvfields) = self.extractDataFields(line)
        cdfid = csvfields[0]
        self.msg.debug(d,cdfid)
        return (d,cdfid)
    
    #example line from a CDF class lst file:
    #g5matz  771734894 (Zaleski, Mathew) matz@cs.toronto.edu
    #
    def extractCdfidName(self, line):
        "returns tuple (cdfid, name)"
        #self.msg.debug("EXTRACT",line)
        tokens_left = line.split('(')[0]  #g5matz  771734894 
        cdfid = tokens_left.split(' ')[0] #g5matz  771734894 (Zaleski, Mathew) matz@cs.toronto.edu

        tokens_right = line.split('(')[1] #Zaleski, Mathew) matz@cs.toronto.edu
        name = tokens_right.split(')')[0]  #Zaleski, Mathew
        #student number is a bit harder, may be one or two blanks
        self.msg.debug("extractDataField name ", name)
        self.msg.debug("extractDataField cdfid ", cdfid)
        return (cdfid, name)
    
        #raise Exception("extractCdfid failed to find data fields in ", line)
        
#         dropped = False
#         for token in tokens[1:]:
#             if len(token) == 0:
#                 continue
#             if token == "d": #students who have dropped are marked such
#                 dropped = True
#                 continue
#             #might be other flags too?
#             if len(token) > 1:
#                 #we've found comman separated fields now
#                 return (dropped, token.split(","))

    def readLines(self):
        lines = []
        for rawline in self.cdf_file:
            line = rawline.rstrip() #how can we figure out what we took off?
            lines.append(line) 
            self.msg.debug("READLINES", line)
        return lines

    def cdfid_to_name(self, cached_lines):
        for line in cached_lines:
            (cdfid,name) = self.extractCdfidName(line)
            self.cdfid_to_name_map[cdfid] = name
        return self.cdfid_to_name_map
    
if __name__ == "__main__" :
    print ("instatiate ClassListFileReader")
    me = CdfClassListFileReader("CSC302H1S")
    ls = me.readLines()
    cdfid_to_name = me.cdfid_to_name(ls)
    for l in ls:
        (cdfid,name) = me.extractCdfidName(l)
        print("cdfid", cdfid, "name", name, "cdfid_to_name", cdfid_to_name[cdfid])
    #print(ls)
        
       
        #os.system( me.interp("cat %(stderrFile)s") )

            
