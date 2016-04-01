'''
Created on Apr 1, 2016

@author: mzaleski
'''
from __future__ import print_function  #allows print as function
import matz_utils
import re
from numpy.oldnumeric.ma import new_take

class GradeFileReader:
    '''
    read grades files
    '''

    def __init__(self, fn):
        '''
        Constructor
        '''
        self.msg = matz_utils.MessagePrinter(False)
        self.msg.setPrefix("GradeFileReader")
        try:
            self.grade_file = open(fn, 'rb')
        except:
            print("eh?",fn)
            self.msg.error("failed to open", fn)
            self.cdfid_to_tut = {}
    
    def skipHeader(self):
        hdr_lines = []
        for line in self.grade_file:
            hdr_lines.append(line.rstrip())
            self.msg.debug("HEADER", line)
            if len(line) == 1:
                return hdr_lines
        raise Exception("oops didn't find empty line at end of grade file header")
    

    def extractCdfid(self, line):
        (d,csvfields) = self.extractDataFields(line)
        cdfid = csvfields[0]
        self.msg.debug(d,cdfid)
        return (d,cdfid)
    
    #a marks file contains lines like: 
    #999521673    c2kosamu,0101,AP
    def extractDataFields(self, line):
        "returns list of csv separated fields"
        #self.msg.debug("EXTRACT",line)
        tokens = line.split(' ')
        dropped = False
        for token in tokens[1:]:
            if len(token) == 0:
                continue
            if token == "d": #students who have dropped are marked such
                dropped = True
                continue
            #might be other flags too?
            if len(token) > 1:
                #we've found comman separated fields now
                return (dropped, token.split(","))
        self.msg.error("extractCdfid failed to find data fields in ", line)
        raise Exception("extractCdfid failed to find data fields in ", line)
        

    def readLines(self):
        lines = []
        for rawline in self.grade_file:
            line = rawline.rstrip() #how can we figure out what we took off?
            lines.append(line) 
            self.msg.debug("READLINES", line)
        return lines
    
    def checkCdfid(self, lines, cdfid_in_map):
        found_problem = False
        list = []
        for line in lines:
            (dropped, cdfid) = self.extractCdfid(line)
            if dropped:
                continue
            if not cdfid in cdfid_in_map:
                found_problem = True
                list.append(cdfid)
        return (found_problem, list)
                
    def readAndAppendColumnFromMap(self,cached_lines, cdfid_to_newcolumn_value_map):
        "read the grades file and append value of dictionary to the csv data values "
        new_lines = []
        for line in cached_lines:
            (dropped, cdfid) = self.extractCdfid(line)
            val = "NA"
            if cdfid in cdfid_to_newcolumn_value_map:
                val = cdfid_to_newcolumn_value_map[cdfid]
                if dropped:
                    self.msg.warning("typo or race condition?", cdfid, "in groups but also marked as dropped") 
            self.msg.verbose("BODY CDFID", cdfid, val)
            new_line = line  +"," + val
            new_lines.append(new_line)
            self.msg.debug("BODY CDFID", new_line)
        return new_lines
            
